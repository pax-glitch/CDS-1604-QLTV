from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class BookForm(FlaskForm):
    title = StringField('Tên sách', validators=[DataRequired(), Length(max=300)])
    isbn = StringField('ISBN', validators=[Length(max=13)])
    publisher_id = SelectField('Nhà xuất bản', coerce=int, validators=[Optional()])
    published_year = IntegerField('Năm xuất bản', validators=[Optional(), NumberRange(min=1900, max=2100)])
    description = TextAreaField('Mô tả')
    total_quantity = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=1)])
    author_ids = SelectMultipleField('Tác giả', coerce=int, validators=[DataRequired()])
    genre_ids = SelectMultipleField('Thể loại', coerce=int, validators=[DataRequired()])
    cover_image = FileField('Ảnh bìa', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Chỉ chấp nhận file ảnh!')])
    submit = SubmitField('Lưu')
