from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

def hash_password(password):
    """Hash a password for storing."""
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return check_password_hash(stored_password, provided_password)

def generate_token(employee_id):
    """Generate JWT token for employee"""
    return create_access_token(
        identity=str(employee_id),
        expires_delta=timedelta(hours=24)
    )