from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class StaffForm(FlaskForm):
    """Form for creating and editing staff members"""
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=50, message='Tên đăng nhập phải từ 3-50 ký tự')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ')
    ])
    
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ tên'),
        Length(min=2, max=200, message='Họ tên phải từ 2-200 ký tự')
    ])
    
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu'),
        Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')
    ])
    
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Vui lòng xác nhận mật khẩu'),
        EqualTo('password', message='Mật khẩu không khớp')
    ])
    
    role = SelectField('Vai trò', choices=[
        ('staff', 'Staff - Nhân viên'),
        ('admin', 'Admin - Quản trị viên'),
        ('superadmin', 'Superadmin - Quản trị cấp cao')
    ], validators=[DataRequired(message='Vui lòng chọn vai trò')])
    
    is_active = BooleanField('Hoạt động', default=True)
    
    avatar = FileField('Ảnh đại diện', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ chấp nhận file ảnh (jpg, jpeg, png, gif)')
    ])
    
    def validate_username(self, username):
        """Validate username is unique"""
        # Skip validation if editing existing user with same username
        if hasattr(self, '_obj') and self._obj and self._obj.username == username.data:
            return
        
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập đã tồn tại')
    
    def validate_email(self, email):
        """Validate email is unique"""
        # Skip validation if editing existing user with same email
        if hasattr(self, '_obj') and self._obj and self._obj.email == email.data:
            return
        
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email đã được sử dụng')
