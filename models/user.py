from database import db
from utils.datetime_utils import get_datetime_now


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=get_datetime_now)
    updated_at = db.Column(db.DateTime, default=get_datetime_now, onupdate=get_datetime_now)
