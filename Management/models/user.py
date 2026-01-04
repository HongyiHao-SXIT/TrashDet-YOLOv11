from app import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="user")

    detections = db.relationship("Detection", backref="user", lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
