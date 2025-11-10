from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Borrow, Book, Reader, Staff
from app.forms.borrow_forms import BorrowForm, ReturnForm, RenewForm
from app.utils.decorators import staff_required
from datetime import datetime, timedelta
from flask import current_app

borrows_bp = Blueprint('borrows', __name__, url_prefix='/borrows')

@borrows_bp.route('/')
@login_required
@staff_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    
    query = Borrow.query
    
    # Search
    if q:
        query = query.join(Reader).join(Book).filter(
            db.or_(
                Reader.full_name.ilike(f'%{q}%'),
                Reader.card_number.ilike(f'%{q}%'),
                Book.title.ilike(f'%{q}%')
            )
        )
    
    # Filter by status
    if status:
        query = query.filter_by(status=status)
    
    # Check and update overdue - No longer needed, auto-updated by property
    
    query = query.order_by(Borrow.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    borrows = pagination.items
    
    # Calculate statistics
    today = datetime.utcnow().date()
    stats = {
        'borrowed': Borrow.query.filter(
            db.or_(Borrow._status == 'borrowed', Borrow._status == 'Borrowed')
        ).count(),
        'overdue': Borrow.query.filter(
            db.or_(Borrow._status == 'overdue', Borrow._status == 'Overdue')
        ).count(),
        'due_soon': Borrow.query.filter(
            Borrow._status.in_(['borrowed', 'Borrowed']),
            Borrow.due_date <= datetime.utcnow() + timedelta(days=3),
            Borrow.due_date >= datetime.utcnow()
        ).count(),
        'returned_today': Borrow.query.filter(
            db.or_(Borrow._status == 'returned', Borrow._status == 'Returned'),
            db.func.date(Borrow.return_date) == today
        ).count()
    }
    
    return render_template('borrows/index.html',
                         borrows=borrows,
                         pagination=pagination,
                         q=q,
                         status=status,
                         days=request.args.get('days', ''),
                         stats=stats)

@borrows_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = BorrowForm()
    
    # Populate choices
    form.reader_id.choices = [(r.id, f"{r.card_number} - {r.full_name}") 
                              for r in Reader.query.filter_by(status='active').order_by(Reader.full_name).all()]
    form.book_id.choices = [(b.id, f"{b.title} (Còn: {b.available_quantity})") 
                           for b in Book.query.filter(Book.available_quantity > 0).order_by(Book.title).all()]
    
    if form.validate_on_submit():
        book = Book.query.get(form.book_id.data)
        reader = Reader.query.get(form.reader_id.data)
        
        # Check availability
        if book.available_quantity <= 0:
            flash('Sách này đã hết!', 'danger')
            return redirect(url_for('borrows.create'))
        
        # Check reader status
        if reader.status != 'active':
            flash('Độc giả này không thể mượn sách!', 'danger')
            return redirect(url_for('borrows.create'))
        
        # Check card expiry
        if reader.is_card_expired:
            flash('Thẻ độc giả đã hết hạn!', 'danger')
            return redirect(url_for('borrows.create'))
        
        # Get staff
        staff = Staff.query.filter_by(user_id=current_user.id).first()
        
        # Create borrow
        borrow = Borrow(
            reader_id=form.reader_id.data,
            book_id=form.book_id.data,
            staff_id=staff.id if staff else None,
            borrow_date=datetime.utcnow(),
            due_date=form.due_date.data,
            status='borrowed'
        )
        
        # Decrease available quantity
        book.available_quantity -= 1
        
        db.session.add(borrow)
        db.session.commit()
        
        flash(f'Đã cho mượn sách "{book.title}" cho {reader.full_name}!', 'success')
        return redirect(url_for('borrows.index'))
    
    # Set default due date
    if request.method == 'GET':
        default_days = current_app.config.get('DEFAULT_BORROW_DAYS', 14)
        form.due_date.data = (datetime.now() + timedelta(days=default_days)).date()
    
    return render_template('borrows/form.html', form=form, title='Cho mượn sách')

@borrows_bp.route('/<int:id>/return', methods=['POST'])
@login_required
@staff_required
def return_book(id):
    try:
        borrow = Borrow.query.get_or_404(id)
        
        if borrow.return_date is not None:
            flash('Sách này đã được trả rồi!', 'warning')
            return redirect(url_for('borrows.index'))
        
        # Update borrow
        borrow.return_date = datetime.utcnow()
        borrow.status = 'returned'
        
        # Increase available quantity
        borrow.book.available_quantity += 1
        
        db.session.commit()
        
        flash(f'Đã xác nhận trả sách "{borrow.book.title}"!', 'success')
        return redirect(url_for('borrows.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi trả sách: {str(e)}', 'danger')
        return redirect(url_for('borrows.index'))

@borrows_bp.route('/<int:id>/renew', methods=['POST'])
@login_required
@staff_required
def renew(id):
    borrow = Borrow.query.get_or_404(id)
    
    # Check if already returned
    if borrow.return_date is not None:
        flash('Không thể gia hạn sách đã trả!', 'danger')
        return redirect(url_for('borrows.index'))
    
    # Check max renew count
    max_renew = current_app.config.get('MAX_RENEW_COUNT', 3)
    if borrow.renew_count >= max_renew:
        flash(f'Đã đạt giới hạn gia hạn ({max_renew} lần)!', 'danger')
        return redirect(url_for('borrows.index'))
    
    # Get renew days from form or use default
    renew_days = int(request.form.get('renew_days', 14))
    
    # Update due date
    borrow.due_date = borrow.due_date + timedelta(days=renew_days)
    borrow.renew_count += 1
    
    # Update status to borrowed (in case it was overdue)
    borrow.status = 'borrowed'
    
    db.session.commit()
    
    flash(f'Đã gia hạn sách "{borrow.book.title}" thêm {renew_days} ngày! Hạn trả mới: {borrow.due_date.strftime("%d/%m/%Y")}', 'success')
    return redirect(url_for('borrows.index'))

@borrows_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
@staff_required
def cancel(id):
    borrow = Borrow.query.get_or_404(id)
    
    if borrow.return_date is not None:
        flash('Không thể hủy phiếu mượn đã trả!', 'danger')
        return redirect(url_for('borrows.index'))
    
    borrow.status = 'Cancelled'
    borrow.book.available_quantity += 1
    
    db.session.commit()
    
    flash('Đã hủy phiếu mượn!', 'success')
    return redirect(url_for('borrows.index'))

@borrows_bp.route('/my-borrows')
@login_required
def my_borrows():
    """For readers to view their borrow history"""
    if not current_user.reader:
        flash('Bạn chưa có thẻ độc giả!', 'warning')
        return redirect(url_for('books.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = Borrow.query.filter_by(reader_id=current_user.reader.id)\
        .order_by(Borrow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    borrows = pagination.items
    
    return render_template('borrows/my_borrows.html', borrows=borrows, pagination=pagination)

@borrows_bp.route('/reader-request/<int:book_id>', methods=['POST'])
@login_required
def reader_request(book_id):
    """Reader requests to borrow a book"""
    # Check if user has reader profile
    if not current_user.reader:
        flash('Bạn chưa có thẻ độc giả! Vui lòng liên hệ thủ thư để đăng ký.', 'warning')
        return redirect(url_for('books.detail', id=book_id))
    
    reader = current_user.reader
    book = Book.query.get_or_404(book_id)
    
    # Check reader status
    if reader.status != 'active':
        flash('Thẻ độc giả của bạn không hoạt động. Vui lòng liên hệ thủ thư!', 'danger')
        return redirect(url_for('books.detail', id=book_id))
    
    # Check card expiry
    if reader.is_card_expired:
        flash('Thẻ độc giả của bạn đã hết hạn! Vui lòng gia hạn thẻ.', 'danger')
        return redirect(url_for('books.detail', id=book_id))
    
    # Check book availability
    if book.available_quantity <= 0:
        flash('Sách này đã hết! Vui lòng thử lại sau.', 'warning')
        return redirect(url_for('books.detail', id=book_id))
    
    # Check if reader already has this book
    existing_borrow = Borrow.query.filter_by(
        reader_id=reader.id,
        book_id=book_id
    ).filter(Borrow.return_date.is_(None)).first()
    
    if existing_borrow:
        flash('Bạn đã mượn cuốn sách này rồi!', 'warning')
        return redirect(url_for('books.detail', id=book_id))
    
    # Get borrow days from form
    borrow_days = int(request.form.get('borrow_days', 14))
    due_date = datetime.utcnow() + timedelta(days=borrow_days)
    
    # Create borrow record
    borrow = Borrow(
        reader_id=reader.id,
        book_id=book_id,
        borrow_date=datetime.utcnow(),
        due_date=due_date,
        status='borrowed'
    )
    
    # Decrease available quantity
    book.available_quantity -= 1
    
    db.session.add(borrow)
    db.session.commit()
    
    flash(f'Đã mượn sách "{book.title}" thành công! Hạn trả: {due_date.strftime("%d/%m/%Y")}', 'success')
    return redirect(url_for('borrows.my_borrows'))
