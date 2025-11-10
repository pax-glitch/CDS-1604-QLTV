from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def roles_required(roles):
    """
    Decorator to restrict access to users with specific roles
    Usage: @roles_required(['admin', 'superadmin'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vui lòng đăng nhập để truy cập trang này.', 'warning')
                return redirect(url_for('auth.login'))
            
            if isinstance(roles, str):
                allowed_roles = [roles]
            else:
                allowed_roles = roles
            
            if not current_user.has_role(allowed_roles):
                flash('Bạn không có quyền truy cập trang này.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to restrict access to admin and superadmin only"""
    return roles_required(['admin', 'superadmin'])(f)

def staff_required(f):
    """Decorator to restrict access to staff, admin and superadmin"""
    return roles_required(['staff', 'admin', 'superadmin'])(f)
