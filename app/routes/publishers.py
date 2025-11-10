from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Publisher
from app.forms.library_forms import PublisherForm
from app.utils.decorators import staff_required

publishers_bp = Blueprint('publishers', __name__, url_prefix='/publishers')

@publishers_bp.route('/')
@login_required
@staff_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = request.args.get('q', '')
    
    query = Publisher.query
    
    if q:
        query = query.filter(Publisher.name.ilike(f'%{q}%'))
    
    query = query.order_by(Publisher.name.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    publishers = pagination.items
    
    return render_template('publishers/index.html', publishers=publishers, pagination=pagination, q=q)

@publishers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create():
    form = PublisherForm()
    if form.validate_on_submit():
        publisher = Publisher(
            name=form.name.data,
            address=form.address.data,
            contact=form.contact.data
        )
        db.session.add(publisher)
        db.session.commit()
        flash('Thêm nhà xuất bản thành công!', 'success')
        return redirect(url_for('publishers.index'))
    
    return render_template('publishers/form.html', form=form, title='Thêm nhà xuất bản')

@publishers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_required
def edit(id):
    publisher = Publisher.query.get_or_404(id)
    form = PublisherForm(obj=publisher)
    
    if form.validate_on_submit():
        publisher.name = form.name.data
        publisher.address = form.address.data
        publisher.contact = form.contact.data
        db.session.commit()
        flash('Cập nhật nhà xuất bản thành công!', 'success')
        return redirect(url_for('publishers.index'))
    
    return render_template('publishers/form.html', form=form, title='Sửa nhà xuất bản', publisher=publisher)

@publishers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@staff_required
def delete(id):
    publisher = Publisher.query.get_or_404(id)
    try:
        db.session.delete(publisher)
        db.session.commit()
        flash('Xóa nhà xuất bản thành công!', 'success')
    except:
        db.session.rollback()
        flash('Không thể xóa nhà xuất bản này!', 'danger')
    
    return redirect(url_for('publishers.index'))
