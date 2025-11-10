from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app import db
from app.models import Borrow, Book, Reader
from app.utils.decorators import admin_required
from sqlalchemy import func, extract
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@admin_required
def index():
    # Get filter dates
    start_date = request.args.get('start_date', (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    # Calculate stats
    stats = {
        'total_books': Book.query.count(),
        'total_readers': Reader.query.count(),
        'borrowed': Borrow.query.filter_by(status='borrowed').count(),
        'overdue': Borrow.query.filter_by(status='overdue').count() + Borrow.query.filter(Borrow.status=='Overdue').count()
    }
    
    # Get overdue books
    overdue_books = Borrow.query.filter(
        db.or_(
            Borrow.status == 'overdue',
            Borrow.status == 'Overdue'
        )
    ).order_by(Borrow.due_date).all()
    
    # Get low stock books (available_quantity <= 2)
    low_stock_books = Book.query.filter(Book.available_quantity <= 2).order_by(Book.available_quantity).all()
    
    return render_template('reports/index.html',
                         stats=stats,
                         overdue_books=overdue_books,
                         low_stock_books=low_stock_books,
                         start_date=start_date,
                         end_date=end_date)

@reports_bp.route('/api/borrows-by-month')
@login_required
@admin_required
def borrows_by_month():
    """API endpoint for borrows chart - last 12 months"""
    # Get data for last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    results = db.session.query(
        extract('year', Borrow.borrow_date).label('year'),
        extract('month', Borrow.borrow_date).label('month'),
        func.count(Borrow.id).label('count')
    ).filter(
        Borrow.borrow_date >= start_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Format data for Chart.js
    labels = []
    data = []
    
    for result in results:
        month_name = f"{int(result.month)}/{int(result.year)}"
        labels.append(month_name)
        data.append(result.count)
    
    return jsonify({
        'labels': labels,
        'datasets': [{
            'label': 'Số lượt mượn',
            'data': data,
            'backgroundColor': 'rgba(79, 70, 229, 0.8)',
            'borderColor': 'rgba(79, 70, 229, 1)',
            'borderWidth': 2
        }]
    })

@reports_bp.route('/api/top-books')
@login_required
@admin_required
def top_books():
    """API endpoint for top borrowed books"""
    limit = request.args.get('limit', 10, type=int)
    
    results = db.session.query(
        Book.title,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow).group_by(Book.id).order_by(func.count(Borrow.id).desc()).limit(limit).all()
    
    labels = [r.title[:30] + '...' if len(r.title) > 30 else r.title for r in results]
    data = [r.borrow_count for r in results]
    
    return jsonify({
        'labels': labels,
        'datasets': [{
            'label': 'Số lượt mượn',
            'data': data,
            'backgroundColor': 'rgba(6, 182, 212, 0.8)',
            'borderColor': 'rgba(6, 182, 212, 1)',
            'borderWidth': 2
        }]
    })

@reports_bp.route('/api/borrow-status')
@login_required
@admin_required
def borrow_status():
    """API endpoint for borrow status distribution"""
    results = db.session.query(
        Borrow.status,
        func.count(Borrow.id).label('count')
    ).group_by(Borrow.status).all()
    
    labels = [r.status for r in results]
    data = [r.count for r in results]
    
    colors = {
        'Borrowed': 'rgba(59, 130, 246, 0.8)',
        'Returned': 'rgba(34, 197, 94, 0.8)',
        'Overdue': 'rgba(239, 68, 68, 0.8)',
        'Cancelled': 'rgba(148, 163, 184, 0.8)'
    }
    
    background_colors = [colors.get(label, 'rgba(148, 163, 184, 0.8)') for label in labels]
    
    return jsonify({
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': background_colors,
            'borderWidth': 2
        }]
    })

@reports_bp.route('/api/borrow-trend')
@login_required
@admin_required
def borrow_trend_api():
    """API endpoint for borrow trend chart"""
    # Get last 12 months data
    results = db.session.query(
        func.strftime('%Y-%m', Borrow.borrow_date).label('month'),
        func.count(Borrow.id).label('count')
    ).filter(
        Borrow.borrow_date >= datetime.utcnow() - timedelta(days=365)
    ).group_by('month').order_by('month').all()
    
    labels = [r.month for r in results]
    values = [r.count for r in results]
    
    return jsonify({
        'labels': labels,
        'values': values
    })

@reports_bp.route('/api/top-books')
@login_required
@admin_required
def top_books_api():
    """API endpoint for top books chart"""
    results = db.session.query(
        Book.title,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow).group_by(Book.id).order_by(func.count(Borrow.id).desc()).limit(10).all()
    
    labels = [r.title[:30] + '...' if len(r.title) > 30 else r.title for r in results]
    values = [r.borrow_count for r in results]
    
    return jsonify({
        'labels': labels,
        'values': values
    })

@reports_bp.route('/api/genre-stats')
@login_required
@admin_required
def genre_stats_api():
    """API endpoint for genre statistics chart"""
    from app.models import Genre, BookGenre
    
    results = db.session.query(
        Genre.name,
        func.count(BookGenre.book_id).label('book_count')
    ).join(BookGenre).group_by(Genre.id).order_by(func.count(BookGenre.book_id).desc()).limit(8).all()
    
    labels = [r.name for r in results]
    values = [r.book_count for r in results]
    
    return jsonify({
        'labels': labels,
        'values': values
    })

@reports_bp.route('/api/top-readers')
@login_required
@admin_required
def top_readers_api():
    """API endpoint for top readers chart"""
    results = db.session.query(
        Reader.full_name,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow).group_by(Reader.id).order_by(func.count(Borrow.id).desc()).limit(10).all()
    
    labels = [r.full_name for r in results]
    values = [r.borrow_count for r in results]
    
    return jsonify({
        'labels': labels,
        'values': values
    })
