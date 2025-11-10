from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Book, Author, Genre, Publisher, BookAuthor, BookGenre
from app.forms.book_forms import BookForm
from app.utils.decorators import staff_required
from app.utils.helpers import save_file, delete_file
import os

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    q = request.args.get('q', '')
    genre_id = request.args.get('genre', type=int)
    publisher_id = request.args.get('publisher', type=int)
    available = request.args.get('available', '')
    
    # Base query with joins
    query = Book.query
    
    # Search
    if q:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{q}%'),
                Book.isbn.ilike(f'%{q}%')
            )
        )
    
    # Filter by genre
    if genre_id:
        query = query.join(BookGenre).filter(BookGenre.genre_id == genre_id)
    
    # Filter by publisher
    if publisher_id:
        query = query.filter(Book.publisher_id == publisher_id)
    
    # Filter by availability
    if available == 'true':
        query = query.filter(Book.available_quantity > 0)
    elif available == 'false':
        query = query.filter(Book.available_quantity == 0)
    
    # Order by newest
    query = query.order_by(Book.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    
    # Get filters data
    genres = Genre.query.order_by(Genre.name).all()
    publishers = Publisher.query.order_by(Publisher.name).all()
    
    return render_template('books/index.html',
                         books=books,
                         pagination=pagination,
                         genres=genres,
                         publishers=publishers,
                         q=q,
                         selected_genre=genre_id,
                         selected_publisher=publisher_id,
                         available=available)

@books_bp.route('/<int:id>')
@login_required
def detail(id):
    book = Book.query.get_or_404(id)
    return render_template('books/detail.html', book=book)

@books_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = BookForm()
    
    # Populate select fields
    form.publisher_id.choices = [(0, '-- Chọn nhà xuất bản --')] + [(p.id, p.name) for p in Publisher.query.order_by(Publisher.name).all()]
    form.author_ids.choices = [(a.id, a.name) for a in Author.query.order_by(Author.name).all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]
    
    if form.validate_on_submit():
        # Create book
        book = Book(
            title=form.title.data,
            isbn=form.isbn.data,
            publisher_id=form.publisher_id.data if form.publisher_id.data != 0 else None,
            published_year=form.published_year.data,
            description=form.description.data,
            total_quantity=form.total_quantity.data,
            available_quantity=form.total_quantity.data
        )
        
        # Handle cover image upload
        if form.cover_image.data:
            filename = save_file(form.cover_image.data, current_app.config['COVER_FOLDER'], f'book_{book.id}_')
            if filename:
                book.cover_image = filename
        
        db.session.add(book)
        db.session.flush()
        
        # Add authors
        for author_id in form.author_ids.data:
            book_author = BookAuthor(book_id=book.id, author_id=author_id)
            db.session.add(book_author)
        
        # Add genres
        for genre_id in form.genre_ids.data:
            book_genre = BookGenre(book_id=book.id, genre_id=genre_id)
            db.session.add(book_genre)
        
        db.session.commit()
        flash('Thêm sách thành công!', 'success')
        return redirect(url_for('books.detail', id=book.id))
    
    return render_template('books/form.html', form=form, title='Thêm sách mới')

@books_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    
    # Populate select fields
    form.publisher_id.choices = [(0, '-- Chọn nhà xuất bản --')] + [(p.id, p.name) for p in Publisher.query.order_by(Publisher.name).all()]
    form.author_ids.choices = [(a.id, a.name) for a in Author.query.order_by(Author.name).all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]
    
    if request.method == 'GET':
        form.publisher_id.data = book.publisher_id if book.publisher_id else 0
        form.author_ids.data = [ba.author_id for ba in book.authors]
        form.genre_ids.data = [bg.genre_id for bg in book.genres]
    
    if form.validate_on_submit():
        old_quantity = book.total_quantity
        borrowed = old_quantity - book.available_quantity
        
        book.title = form.title.data
        book.isbn = form.isbn.data
        book.publisher_id = form.publisher_id.data if form.publisher_id.data != 0 else None
        book.published_year = form.published_year.data
        book.description = form.description.data
        book.total_quantity = form.total_quantity.data
        book.available_quantity = form.total_quantity.data - borrowed
        
        # Handle cover image
        if form.cover_image.data:
            # Delete old cover
            if book.cover_image:
                old_path = os.path.join(current_app.config['COVER_FOLDER'], book.cover_image)
                delete_file(old_path)
            
            # Save new cover
            filename = save_file(form.cover_image.data, current_app.config['COVER_FOLDER'], f'book_{book.id}_')
            if filename:
                book.cover_image = filename
        
        # Update authors
        BookAuthor.query.filter_by(book_id=book.id).delete()
        for author_id in form.author_ids.data:
            book_author = BookAuthor(book_id=book.id, author_id=author_id)
            db.session.add(book_author)
        
        # Update genres
        BookGenre.query.filter_by(book_id=book.id).delete()
        for genre_id in form.genre_ids.data:
            book_genre = BookGenre(book_id=book.id, genre_id=genre_id)
            db.session.add(book_genre)
        
        db.session.commit()
        flash('Cập nhật sách thành công!', 'success')
        return redirect(url_for('books.detail', id=book.id))
    
    return render_template('books/form.html', form=form, title='Sửa thông tin sách', book=book)

@books_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(id):
    book = Book.query.get_or_404(id)
    
    # Check if book is borrowed
    if book.available_quantity < book.total_quantity:
        flash('Không thể xóa sách đang được mượn!', 'danger')
        return redirect(url_for('books.index'))
    
    try:
        # Delete cover image
        if book.cover_image:
            cover_path = os.path.join(current_app.config['COVER_FOLDER'], book.cover_image)
            delete_file(cover_path)
        
        db.session.delete(book)
        db.session.commit()
        flash('Xóa sách thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa sách này!', 'danger')
    
    return redirect(url_for('books.index'))
