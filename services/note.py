from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import NoteModel


# =====================
# ==== Create Note ====
# =====================
def create_note(new_note_data: dict, user_id: int):
    title: str | None = new_note_data.get("title")
    content: str = new_note_data.get("content", "")
    # ----
    if not isinstance(title, str) or not title or not title.strip():
        return None, "Title is required and must be a string."
    if content and not isinstance(content, str):
        return None, "Content must be a string."
    # ----
    new_note = NoteModel()
    new_note.user_id = user_id
    new_note.title = title.strip()
    new_note.content = content
    # ----
    try:
        db.session.add(new_note)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, "Title is already_exists"
    except SQLAlchemyError:
        db.session.rollback()
        return None, "An error occurred creating the store."
    # ----
    as_json = {
        "id": new_note.id,
        "title": new_note.title,
        "content": new_note.content,
        "created_at": new_note.created_at.isoformat(),
        "updated_at": new_note.updated_at.isoformat(),
    }
    return as_json, "Note created successfully"


# =======================
# ==== Get All Notes ====
# =======================
def get_all_notes(user_id: int):
    notes = NoteModel.query.filter_by(user_id=user_id).all()
    if not notes:
        return [], "No notes found."
    as_json = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
        for note in notes
    ]

    return as_json, None


# =================================
# === Get a specific note by ID ===
# =================================
def get_note_by_id(note_id: int, user_id: int):
    note: NoteModel | None = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
    if note is None:
        return None, "Note not found."
    as_json = {
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
    }
    return as_json, None


# ====================================
# === Update a specific note by ID ===
# ====================================
def update_note_by_id(note_id: int, updated_data: dict,user_id:int):
    note: NoteModel | None = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
    if note is None:
        return None, "Note not found."
    # ----
    title_x, content_x = False, False
    title: str | None = updated_data.get("title", None)
    content: str | None = updated_data.get("content", None)
    # ----
    if title is None and content is None:
        return None, "At least one field must be updated."

    if title is not None:
        if not isinstance(title, str):
            return None, "Title must be a string."
        title = title.strip()
        if not title:
            return None, "Title cannot be empty."
        note.title = title
        title_x = True

    if content is not None:
        if not isinstance(content, str):
            return None, "Content must be a string."
        note.content = content
        content_x = True
    # ----
    try:
        if title_x or content_x:
            db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return None, "Title is already_exists"

    except SQLAlchemyError:
        db.session.rollback()
        return None, "An error occurred updating the note."
    # ----
    if title_x and content_x:
        message = "Note (title and content) updated successfully."
    elif title_x:
        message = "Note (only title) updated successfully."
    elif content_x:
        message = "Note (only content) updated successfully."
    else:
        message = "Note not updated."

    as_json = {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }

    return as_json, message


# ====================================
# === Delete a specific note by ID ===
# ====================================
def delete_note_by_id(note_id: int,user_id:int):
    note: NoteModel | None = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
    if note is None:
        return None, "Note not found."
    try:
        db.session.delete(note)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return None, "An error occurred deleting the note."
    return {}, "Note deleted successfully."
