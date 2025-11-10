from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ReaderForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Số điện thoại', validators=[Length(max=20)])
    address = TextAreaField('Địa chỉ')
    date_of_birth = DateField('Ngày sinh', validators=[Optional()], format='%Y-%m-%d')
    card_expiry_date = DateField('Ngày hết hạn thẻ', validators=[DataRequired()], format='%Y-%m-%d')
    status = SelectField('Trạng thái', choices=[
        ('active', 'Hoạt động'),
        ('blocked', 'Bị khóa'),
        ('expired', 'Hết hạn')
    ])
    submit = SubmitField('Lưu')
