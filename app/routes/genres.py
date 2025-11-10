from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Genre
from app.forms.library_forms import GenreForm
from app.utils.decorators import staff_required

genres_bp = Blueprint('genres', __name__, url_prefix='/genres')

@genres_bp.route('/')
@login_required
@staff_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '')
    
    query = Genre.query
    
    if q:
        query = query.filter(Genre.name.ilike(f'%{q}%'))
    
    query = query.order_by(Genre.name.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    genres = pagination.items
    
    return render_template('genres/index.html', genres=genres, pagination=pagination, q=q)

@genres_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data, description=form.description.data)
        db.session.add(genre)
        db.session.commit()
        flash('Thêm thể loại thành công!', 'success')
        return redirect(url_for('genres.index'))
    
    return render_template('genres/form.html', form=form, title='Thêm thể loại')

@genres_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(id):
    genre = Genre.query.get_or_404(id)
    form = GenreForm(obj=genre)
    
    if form.validate_on_submit():
        genre.name = form.name.data
        genre.description = form.description.data
        db.session.commit()
        flash('Cập nhật thể loại thành công!', 'success')
        return redirect(url_for('genres.index'))
    
    return render_template('genres/form.html', form=form, title='Sửa thể loại', genre=genre)

@genres_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(id):
    genre = Genre.query.get_or_404(id)
    try:
        db.session.delete(genre)
        db.session.commit()
        flash('Xóa thể loại thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa thể loại này!', 'danger')
    
    return redirect(url_for('genres.index'))
