from datetime import datetime, timezone

from database import db


def get_date_now() -> datetime:

    return datetime.now(timezone.utc)


class NoteModel(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_date_now)
    updated_at = db.Column(db.DateTime, default=get_date_now, onupdate=get_date_now)
