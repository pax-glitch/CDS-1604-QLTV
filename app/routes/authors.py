from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Author
from app.forms.library_forms import AuthorForm
from app.utils.decorators import staff_required

authors_bp = Blueprint('authors', __name__, url_prefix='/authors')

@authors_bp.route('/')
@login_required
@staff_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '')
    sort = request.args.get('sort', 'name_asc')
    
    # Base query
    query = Author.query
    
    # Search
    if q:
        query = query.filter(Author.name.ilike(f'%{q}%'))
    
    # Sort
    if sort == 'name_asc':
        query = query.order_by(Author.name.asc())
    elif sort == 'name_desc':
        query = query.order_by(Author.name.desc())
    elif sort == 'newest':
        query = query.order_by(Author.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Author.created_at.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    authors = pagination.items
    
    return render_template('authors/index.html', 
                         authors=authors, 
                         pagination=pagination,
                         q=q,
                         sort=sort)

@authors_bp.route('/<int:id>')
@login_required
@staff_required
def detail(id):
    author = Author.query.get_or_404(id)
    return render_template('authors/detail.html', author=author)

@authors_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = AuthorForm()
    if form.validate_on_submit():
        author = Author(
            name=form.name.data,
            bio=form.bio.data
        )
        db.session.add(author)
        db.session.commit()
        flash('Thêm tác giả thành công!', 'success')
        return redirect(url_for('authors.index'))
    
    return render_template('authors/form.html', form=form, title='Thêm tác giả')

@authors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(id):
    author = Author.query.get_or_404(id)
    form = AuthorForm(obj=author)
    
    if form.validate_on_submit():
        author.name = form.name.data
        author.bio = form.bio.data
        db.session.commit()
        flash('Cập nhật tác giả thành công!', 'success')
        return redirect(url_for('authors.index'))
    
    return render_template('authors/form.html', form=form, title='Sửa tác giả', author=author)

@authors_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(id):
    author = Author.query.get_or_404(id)
    try:
        db.session.delete(author)
        db.session.commit()
        flash('Xóa tác giả thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Không thể xóa tác giả này vì đang có sách liên quan!', 'danger')
    
    return redirect(url_for('authors.index'))
