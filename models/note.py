from database import db
from utils.datetime_utils import get_datetime_now


class NoteModel(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False )
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_datetime_now)
    updated_at = db.Column(db.DateTime, default=get_datetime_now, onupdate=get_datetime_now)
