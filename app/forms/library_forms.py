from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class AuthorForm(FlaskForm):
    name = StringField('Tên tác giả', validators=[DataRequired(), Length(max=200)])
    bio = TextAreaField('Tiểu sử')
    submit = SubmitField('Lưu')

class GenreForm(FlaskForm):
    name = StringField('Tên thể loại', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Mô tả')
    submit = SubmitField('Lưu')

class PublisherForm(FlaskForm):
    name = StringField('Tên nhà xuất bản', validators=[DataRequired(), Length(max=200)])
    address = TextAreaField('Địa chỉ')
    contact = StringField('Liên hệ', validators=[Length(max=200)])
    submit = SubmitField('Lưu')
