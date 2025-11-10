"""
Forms package - exports all form classes
"""

from app.forms.auth_forms import LoginForm, RegisterForm
from app.forms.book_forms import BookForm
from app.forms.reader_forms import ReaderForm
from app.forms.staff_forms import StaffForm
from app.forms.library_forms import AuthorForm, GenreForm, PublisherForm

__all__ = [
    'LoginForm',
    'RegisterForm',
    'BookForm',
    'ReaderForm',
    'StaffForm',
    'AuthorForm',
    'GenreForm',
    'PublisherForm'
]
