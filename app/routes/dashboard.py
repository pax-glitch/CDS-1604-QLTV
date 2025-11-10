from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Book, Reader, Borrow, User, Staff
from app.utils.decorators import staff_required
from sqlalchemy import func, extract
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
@staff_required
def index():
    # Statistics
    total_books = Book.query.count()
    total_readers = Reader.query.filter_by(status='active').count()
    total_borrowed = Borrow.query.filter_by(status='Borrowed').count()
    total_overdue = Borrow.query.filter_by(status='Overdue').count()
    
    # Books stats
    books_borrowed = db.session.query(func.sum(Book.total_quantity - Book.available_quantity)).scalar() or 0
    books_available = db.session.query(func.sum(Book.available_quantity)).scalar() or 0
    
    # Recent borrows
    recent_borrows = Borrow.query.order_by(Borrow.created_at.desc()).limit(10).all()
    
    # Top borrowed books
    top_books = db.session.query(
        Book,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow).group_by(Book.id).order_by(func.count(Borrow.id).desc()).limit(5).all()
    
    # Overdue borrows
    overdue_borrows = Borrow.query.filter(
        Borrow.return_date.is_(None),
        Borrow.due_date < datetime.utcnow()
    ).order_by(Borrow.due_date).limit(10).all()
    
    # Update overdue status
    for borrow in overdue_borrows:
        if borrow.status != 'Overdue':
            borrow.status = 'Overdue'
    db.session.commit()
    
    stats = {
        'total_books': total_books,
        'total_readers': total_readers,
        'total_borrowed': total_borrowed,
        'total_overdue': total_overdue,
        'books_borrowed': books_borrowed,
        'books_available': books_available
    }
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_borrows=recent_borrows,
                         top_books=top_books,
                         overdue_borrows=overdue_borrows)
