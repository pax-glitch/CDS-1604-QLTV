from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Reader
from app.forms.auth_forms import LoginForm, RegisterForm
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.is_active and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Chào mừng {user.full_name}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role in ['superadmin', 'admin', 'staff']:
                return redirect(url_for('dashboard.index'))
            else:
                return redirect(url_for('books.index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            password=hashed_password,
            role='reader'
        )
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create reader card
        card_number = f"LIB{datetime.now().year}{user.id:05d}"
        reader = Reader(
            user_id=user.id,
            card_number=card_number,
            full_name=form.full_name.data,
            email=form.email.data,
            card_issue_date=datetime.now().date(),
            card_expiry_date=(datetime.now() + timedelta(days=365)).date(),
            status='active'
        )
        db.session.add(reader)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))
