from datetime import datetime

def register_filters(app):
    """Register custom Jinja2 filters"""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        """Format a datetime object"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%d/%m/%Y'):
        """Format a date object"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('status_badge')
    def status_badge(status):
        """Return Bootstrap badge class for status"""
        badges = {
            'active': 'success',
            'blocked': 'danger',
            'expired': 'warning',
            'Borrowed': 'primary',
            'Returned': 'success',
            'Overdue': 'danger',
            'Cancelled': 'secondary',
            'Pending': 'warning'
        }
        return badges.get(status, 'secondary')
    
    @app.template_filter('role_badge')
    def role_badge(role):
        """Return Bootstrap badge class for user role"""
        badges = {
            'superadmin': 'danger',
            'admin': 'warning',
            'staff': 'info',
            'reader': 'success'
        }
        return badges.get(role, 'secondary')
