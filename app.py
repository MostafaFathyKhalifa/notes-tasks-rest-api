from flask import Flask, request
from flask_cors import CORS
from flask_smorest import Api  # noqa: F401
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import NoteModel

# === App Setup ===
app = Flask(__name__)
CORS(app)  # السماح بالوصول من أي مصدر (Cross-Origin Resource Sharing
URL_PREFIX = "/api/v1"
# =========================
# == App Configuration ==
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# =========================
# === Initialize Database and API ===
db.init_app(app)
# api = Api(app)
# ==========================
# == Create Database Tables ==
with app.app_context():
    db.create_all()


# =========================
# == Helper Functions ==
def url_prefix(endpoint: str = "") -> str:
    return f"{URL_PREFIX}{endpoint}"


def get_date_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


# ========================
# === EndPoints ===
@app.get(url_prefix())
def index():
    return {"message": "Welcome to the API!"}, 200


@app.get(url_prefix("/health"))
def health():
    return {"status": "ok"}, 200


# == Get all notes ==
@app.get(url_prefix("/notes"))
def get_notes():
    notes = NoteModel.query.all()
    as_json = {
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
            }
            for note in notes
        ]
    }
    return as_json, 200


# == Create a new note ==
@app.post(url_prefix("/notes"))
def create_note():
    new_note_data = request.get_json(silent=True)
    if not new_note_data:
        return {"message": "Invalid JSON data."}, 400
    if not isinstance(new_note_data, dict):
        return {"message": "Request body must be a JSON object"}, 400
    title: str | None = new_note_data.get("title")
    content: str | None = new_note_data.get("content", "")
    if not isinstance(title, str) or not title or not title.strip():
        return {"message": "Title is required and must be a string."}, 400
    if content and not isinstance(content, str):
        return {"message": "Content must be a string."}, 400
    new_note = NoteModel()
    new_note.title = title.strip()
    new_note.content = content
    try:
        db.session.add(new_note)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "Title is already_exists"}, 409
    except SQLAlchemyError:
        db.session.rollback()
        return {"message": "An error occurred creating the store."}, 500

    return {
        "message": "Note created successfully",
        "note": {
            "id": new_note.id,
            "title": new_note.title.strip(),
            "content": new_note.content,
            "created_at": new_note.created_at.isoformat(),
            "updated_at": new_note.updated_at.isoformat(),
        },
    }, 201


# == Get a specific note by ID ==
@app.get(url_prefix("/notes/<int:note_id>"))
def get_note(note_id: int):
    note: NoteModel | None = NoteModel.query.get(note_id)
    if not note:
        return {"message": "Note not found."}, 404
    as_json = {
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
    }
    return as_json, 200


# == Update a specific note by ID ==
@app.patch(url_prefix("/notes/<int:note_id>"))
def update_note(note_id: int):
    updated_data = request.get_json(silent=True)
    note = NoteModel.query.get(note_id)
    title_x, content_x = False, False
    if not note:
        return {"message": "Note not found."}, 404
    if updated_data is None:
        return {"message": "Invalid JSON data."}, 400
    if not isinstance(updated_data, dict):
        return {"message": "Request body must be a JSON object"}, 400

    title: str | None = updated_data.get("title", None)
    content: str | None = updated_data.get("content", None)
    # ====
    if title is None and content is None:
        return {"message": "At least one field must be updated"}, 400

    if title is not None:
        if not isinstance(title, str):
            return {"message": "Title must be a string."}, 400

        if title.strip():
            note.title = title.strip()
            title_x = True

    if content is not None:
        if not isinstance(content, str):
            return {"message": "Content must be a string."}, 400
        note.content = content
        content_x = True
    # =====
    try:
        if title_x or content_x :
            db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return {"message": "Title already exists."}, 409

    except SQLAlchemyError:
        db.session.rollback()
        return {"message": "An error occurred updating the note."}, 500

    if title_x and content_x:
        message = "Note (title and content) updated successfully"
    elif title_x or content_x:
        who = "title" if title_x else "content"
        message = f"Note (Only {who}) updated successfully"
    else:
        message = "Note not updated"
    return {
        "message": message,
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        },
    }, 200


# == Delete a specific note by ID ==
@app.delete(url_prefix("/notes/<int:note_id>"))
def delete_note(note_id: int):
    note = NoteModel.query.get(note_id)
    if not note:
        return {"message": "Note not found."}, 404
    try:
        db.session.delete(note)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return {"message": "An error occurred deleting the note."}, 500

    return {"message": "Note deleted successfully."}, 200
