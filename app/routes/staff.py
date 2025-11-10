from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import User, Staff
from app.utils.decorators import admin_required
from app.forms import StaffForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/')
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    q = request.args.get('q', '')
    role = request.args.get('role', '')
    
    query = User.query.filter(User.role.in_(['staff', 'admin', 'superadmin']))
    
    if q:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{q}%'),
                User.full_name.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%')
            )
        )
    
    if role:
        query = query.filter_by(role=role)
    
    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template('staff/index.html', users=users, pagination=pagination, q=q, role=role)

@staff_bp.route('/<int:id>')
@login_required
@admin_required
def detail(id):
    user = User.query.get_or_404(id)
    return render_template('staff/detail.html', user=user)

@staff_bp.route('/<int:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(id):
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'kích hoạt' if user.is_active else 'vô hiệu hóa'
    flash(f'Đã {status} tài khoản {user.username}!', 'success')
    return redirect(url_for('staff.index'))

@staff_bp.route('/<int:id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_role(id):
    user = User.query.get_or_404(id)
    new_role = request.form.get('role')
    
    if new_role not in ['staff', 'admin', 'superadmin']:
        flash('Vai trò không hợp lệ!', 'danger')
        return redirect(url_for('staff.detail', id=id))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'Đã cập nhật vai trò cho {user.username}!', 'success')
    return redirect(url_for('staff.detail', id=id))

@staff_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = StaffForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('staff/form.html', form=form, user=None)
        
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('staff/form.html', form=form, user=None)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            role=form.role.data,
            is_active=form.is_active.data
        )
        
        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            if file.filename:
                filename = secure_filename(file.filename)
                filename = f"{user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                avatar_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads', 'avatars')
                os.makedirs(avatar_folder, exist_ok=True)
                file.save(os.path.join(avatar_folder, filename))
                user.avatar = filename
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Đã tạo tài khoản {user.username} thành công!', 'success')
        return redirect(url_for('staff.index'))
    
    return render_template('staff/form.html', form=form, user=None)

@staff_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = User.query.get_or_404(id)
    form = StaffForm(obj=user)
    
    # Remove password fields for edit
    del form.password
    del form.confirm_password
    
    if form.validate_on_submit():
        # Check if email is changed and already exists
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('staff/form.html', form=form, user=user)
        
        user.email = form.email.data
        user.full_name = form.full_name.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            if file.filename:
                filename = secure_filename(file.filename)
                filename = f"{user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                avatar_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads', 'avatars')
                os.makedirs(avatar_folder, exist_ok=True)
                file.save(os.path.join(avatar_folder, filename))
                
                # Delete old avatar
                if user.avatar:
                    old_avatar_path = os.path.join(avatar_folder, user.avatar)
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                
                user.avatar = filename
        
        db.session.commit()
        flash(f'Đã cập nhật thông tin {user.username}!', 'success')
        return redirect(url_for('staff.index'))
    
    return render_template('staff/form.html', form=form, user=user)

@staff_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    user = User.query.get_or_404(id)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        flash('Không thể xóa tài khoản của chính mình!', 'danger')
        return redirect(url_for('staff.index'))
    
    # Cannot delete superadmin
    if user.role == 'superadmin':
        flash('Không thể xóa tài khoản superadmin!', 'danger')
        return redirect(url_for('staff.index'))
    
    # Delete avatar
    if user.avatar:
        avatar_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads', 'avatars', user.avatar)
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Đã xóa tài khoản {username}!', 'success')
    return redirect(url_for('staff.index'))
