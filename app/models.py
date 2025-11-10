from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False, default='reader')  # superadmin|admin|staff|reader
    avatar = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('Staff', backref='user', uselist=False, cascade='all, delete-orphan')
    reader = db.relationship('Reader', backref='user', uselist=False, cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def has_role(self, roles):
        """Check if user has one of the specified roles"""
        if isinstance(roles, str):
            roles = [roles]
        return self.role in roles

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    books = db.relationship('BookAuthor', back_populates='author', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Author {self.name}>'

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    books = db.relationship('BookGenre', back_populates='genre', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Genre {self.name}>'

class Publisher(db.Model):
    __tablename__ = 'publishers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    address = db.Column(db.Text)
    contact = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', backref='publisher', lazy='dynamic')
    
    def __repr__(self):
        return f'<Publisher {self.name}>'

class Reader(db.Model):
    __tablename__ = 'readers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    card_number = db.Column(db.String(50), unique=True)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    card_issue_date = db.Column(db.Date)
    card_expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active|blocked|expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    borrows = db.relationship('Borrow', backref='reader', lazy='dynamic')
    
    def __repr__(self):
        return f'<Reader {self.full_name}>'
    
    @property
    def is_card_expired(self):
        """Check if library card is expired"""
        if self.card_expiry_date:
            return self.card_expiry_date < datetime.utcnow().date()
        return False

class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    position = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    borrows = db.relationship('Borrow', backref='staff', lazy='dynamic')
    
    def __repr__(self):
        return f'<Staff {self.user.full_name}>'

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    published_year = db.Column(db.Integer)
    cover_image = db.Column(db.String(255))
    description = db.Column(db.Text)
    total_quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    authors = db.relationship('BookAuthor', back_populates='book', cascade='all, delete-orphan')
    genres = db.relationship('BookGenre', back_populates='book', cascade='all, delete-orphan')
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_quantity > 0

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)
    
    # Relationships
    book = db.relationship('Book', back_populates='authors')
    author = db.relationship('Author', back_populates='books')

class BookGenre(db.Model):
    __tablename__ = 'book_genres'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    
    # Relationships
    book = db.relationship('Book', back_populates='genres')
    genre = db.relationship('Genre', back_populates='books')

class Borrow(db.Model):
    __tablename__ = 'borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    _status = db.Column('status', db.String(20), default='borrowed')  # borrowed|returned|overdue|cancelled
    renew_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Borrow {self.id}>'
    
    @property
    def status(self):
        """Auto-update status based on current state"""
        # If returned, status is returned
        if self.return_date is not None:
            return 'returned'
        # If overdue
        if self.due_date and self.due_date < datetime.utcnow():
            if self._status != 'overdue':
                self._status = 'overdue'
            return 'overdue'
        # Otherwise borrowed
        return 'borrowed'
    
    @status.setter
    def status(self, value):
        """Set status"""
        self._status = value.lower() if value else 'borrowed'
    
    @property
    def is_overdue(self):
        """Check if borrow is overdue"""
        if self.return_date is None and self.due_date:
            return self.due_date < datetime.utcnow()
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (datetime.utcnow() - self.due_date).days
        return 0
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.return_date is None and self.due_date:
            days = (self.due_date - datetime.utcnow()).days
            return max(0, days)
        return 0

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Log {self.action}>'
