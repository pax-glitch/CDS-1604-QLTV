from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class BorrowForm(FlaskForm):
    reader_id = SelectField('Độc giả', coerce=int, validators=[DataRequired()])
    book_id = SelectField('Sách', coerce=int, validators=[DataRequired()])
    due_date = DateField('Ngày hẹn trả', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Xác nhận mượn')

class ReturnForm(FlaskForm):
    submit = SubmitField('Xác nhận trả')

class RenewForm(FlaskForm):
    due_date = DateField('Ngày hẹn trả mới', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Gia hạn')
