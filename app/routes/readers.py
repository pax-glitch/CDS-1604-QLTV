from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from app import db
from app.models import Reader, User, Borrow
from app.forms.reader_forms import ReaderForm
from app.utils.decorators import staff_required
from datetime import datetime, timedelta
import io
import csv

readers_bp = Blueprint('readers', __name__, url_prefix='/readers')

@readers_bp.route('/')
@login_required
@staff_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    
    query = Reader.query
    
    # Search
    if q:
        query = query.filter(
            db.or_(
                Reader.full_name.ilike(f'%{q}%'),
                Reader.card_number.ilike(f'%{q}%'),
                Reader.email.ilike(f'%{q}%')
            )
        )
    
    # Filter by status
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Reader.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    readers = pagination.items
    
    return render_template('readers/index.html',
                         readers=readers,
                         pagination=pagination,
                         q=q,
                         status=status,
                         today=datetime.utcnow().date())

@readers_bp.route('/<int:id>')
@login_required
@staff_required
def detail(id):
    reader = Reader.query.get_or_404(id)
    # Get borrow history
    borrows = Borrow.query.filter_by(reader_id=id).order_by(Borrow.created_at.desc()).all()
    return render_template('readers/detail.html', reader=reader, borrows=borrows, today=datetime.utcnow().date())

@readers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = ReaderForm()
    
    if form.validate_on_submit():
        # Generate card number
        card_number = f"LIB{datetime.now().year}{Reader.query.count() + 1:05d}"
        
        reader = Reader(
            card_number=card_number,
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            card_issue_date=datetime.now().date(),
            card_expiry_date=form.card_expiry_date.data,
            status=form.status.data
        )
        
        db.session.add(reader)
        db.session.commit()
        flash('Thêm độc giả thành công!', 'success')
        return redirect(url_for('readers.detail', id=reader.id))
    
    # Set default expiry date (1 year from now)
    if request.method == 'GET':
        form.card_expiry_date.data = (datetime.now() + timedelta(days=365)).date()
    
    return render_template('readers/form.html', form=form, title='Thêm độc giả')

@readers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(id):
    reader = Reader.query.get_or_404(id)
    form = ReaderForm(obj=reader)
    
    if form.validate_on_submit():
        reader.full_name = form.full_name.data
        reader.email = form.email.data
        reader.phone = form.phone.data
        reader.address = form.address.data
        reader.date_of_birth = form.date_of_birth.data
        reader.card_expiry_date = form.card_expiry_date.data
        reader.status = form.status.data
        
        db.session.commit()
        flash('Cập nhật thông tin độc giả thành công!', 'success')
        return redirect(url_for('readers.detail', id=reader.id))
    
    return render_template('readers/form.html', form=form, title='Sửa thông tin độc giả', reader=reader)

@readers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(id):
    reader = Reader.query.get_or_404(id)
    
    # Check if reader has active borrows
    active_borrows = Borrow.query.filter_by(reader_id=id, status='Borrowed').count()
    if active_borrows > 0:
        flash('Không thể xóa độc giả đang có sách mượn!', 'danger')
        return redirect(url_for('readers.index'))
    
    try:
        db.session.delete(reader)
        db.session.commit()
        flash('Xóa độc giả thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa độc giả này!', 'danger')
    
    return redirect(url_for('readers.index'))

@readers_bp.route('/export')
@login_required
@staff_required
def export():
    """Export readers to CSV"""
    readers = Reader.query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Mã thẻ', 'Họ tên', 'Email', 'Điện thoại', 'Ngày sinh', 'Ngày cấp thẻ', 'Ngày hết hạn', 'Trạng thái'])
    
    # Write data
    for reader in readers:
        writer.writerow([
            reader.card_number,
            reader.full_name,
            reader.email or '',
            reader.phone or '',
            reader.date_of_birth.strftime('%d/%m/%Y') if reader.date_of_birth else '',
            reader.card_issue_date.strftime('%d/%m/%Y') if reader.card_issue_date else '',
            reader.card_expiry_date.strftime('%d/%m/%Y') if reader.card_expiry_date else '',
            reader.status
        ])
    
    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'readers_{datetime.now().strftime("%Y%m%d")}.csv'
    )
