import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder, prefix=''):
    """
    Save uploaded file with secure filename
    Returns: filename or None if failed
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid name conflicts
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{prefix}{timestamp}{ext}" if prefix else f"{timestamp}_{filename}"
        
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filename
    return None

def delete_file(filepath):
    """Delete file if it exists"""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except:
            return False
    return False
