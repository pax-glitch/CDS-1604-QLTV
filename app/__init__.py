from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Application factory"""
    # Get parent directory (project root)
    import os
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)
    os.makedirs(app.config['COVER_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.authors import authors_bp
    from app.routes.genres import genres_bp
    from app.routes.publishers import publishers_bp
    from app.routes.books import books_bp
    from app.routes.readers import readers_bp
    from app.routes.staff import staff_bp
    from app.routes.borrows import borrows_bp
    from app.routes.profile import profile_bp
    from app.routes.reports import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(genres_bp)
    app.register_blueprint(publishers_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(readers_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(borrows_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(reports_bp)
    
    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)
    
    # Add context processor for CSRF token
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Add root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role in ['superadmin', 'admin', 'staff']:
                return redirect(url_for('dashboard.index'))
            else:
                return redirect(url_for('books.index'))
        return redirect(url_for('auth.login'))
    
    return app
