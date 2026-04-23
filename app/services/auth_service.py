from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db


def create_user(username, password, role='staff'):
    """Create a new user with hashed password."""
    pw_hash = generate_password_hash(password)
    user = User(username=username, password_hash=pw_hash, role=role)
    db.session.add(user)
    db.session.commit()
    return user


def verify_user(username, password):
    """Verify credentials. Returns User object or None."""
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
