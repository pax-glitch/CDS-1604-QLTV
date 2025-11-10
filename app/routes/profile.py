from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import User
from app.forms.auth_forms import ChangePasswordForm
from app.utils.helpers import save_file, delete_file
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

class ProfileForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Ảnh đại diện', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ chấp nhận file ảnh!')])
    submit = SubmitField('Cập nhật')

@profile_bp.route('/')
@login_required
def index():
    return render_template('profile/index.html')

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        
        # Handle avatar upload
        if form.avatar.data:
            # Delete old avatar
            if current_user.avatar:
                old_path = os.path.join(current_app.config['AVATAR_FOLDER'], current_user.avatar)
                delete_file(old_path)
            
            # Save new avatar
            filename = save_file(form.avatar.data, current_app.config['AVATAR_FOLDER'], f'user_{current_user.id}_')
            if filename:
                current_user.avatar = filename
        
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Check old password
        if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
            flash('Mật khẩu cũ không đúng!', 'danger')
            return render_template('profile/change_password.html', form=form)
        
        # Update password
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/change_password.html', form=form)
