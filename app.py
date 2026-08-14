from flask import Flask, request
from flask_cors import CORS

from fack_db import db

# ========================
app = Flask(__name__)
CORS(app)  # السماح بالوصول من أي مصدر (Cross-Origin Resource Sharing

URL_PREFIX = "/api/v1"


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
    notes = db.get("notes", [])
    return {"notes": notes}, 200


# == Create a new note ==
@app.post(url_prefix("/notes"))
def create_note():
    new_note = request.get_json(silent=True)
    if not new_note:
        return {"message": "Invalid JSON data."}, 400
    if not isinstance(new_note, dict):
        return {"message": "Request body must be a JSON object"}, 400
    title = new_note.get("title")
    content = new_note.get("content")
    if not title or not isinstance(title, str):
        return {"message": "Title is required and must be a string."}, 400
    if content and not isinstance(content, str):
        return {"message": "Content must be a string."}, 400
    notes = db.get("notes", [])
    new_note["id"] = max((note.get("id", 0) for note in db["notes"]), default=0) + 1
    new_note["created_at"] = get_date_now()
    new_note["updated_at"] = new_note["created_at"]
    notes.append(new_note)
    return {"note": new_note}, 201


# == Get a specific note by ID ==
@app.get(url_prefix("/notes/<int:note_id>"))
def get_note(note_id: int):
    notes = db.get("notes", [])
    for note in notes:
        if note.get("id") == note_id:
            return {"note": note}, 200
    return {"message": "Note not found."}, 404


# == Update a specific note by ID ==
@app.patch(url_prefix("/notes/<int:note_id>"))
def update_note(note_id: int):
    updated_data = request.get_json(silent=True)
    if not updated_data:
        return {"message": "Invalid JSON data."}, 400
    if not isinstance(updated_data, dict):
        return {"message": "Request body must be a JSON object"}, 400

    title = updated_data.get("title")
    content = updated_data.get("content")
    if not title and not content:
        return {"message": "At least one of title or content must be provided."}, 400
    if not isinstance(title, str | None) or not isinstance(content, str | None):
        return {"message": "Title and content must be strings."}, 400
    notes = db.get("notes", [])
    for note in notes:
        if note.get("id") == note_id:
            note["title"] = title if title else note.get("title")
            note["content"] = content if content else note.get("content")
            note["updated_at"] = get_date_now()
            return {"note": note}, 200
    return {"message": "Note not found."}, 404


# == Delete a specific note by ID ==
@app.delete(url_prefix("/notes/<int:note_id>"))
def delete_note(note_id: int):
    notes = db.get("notes", [])
    for note in notes:
        if note.get("id") == note_id:
            notes.remove(note)
            return {"message": "Note deleted."}, 200
    return {"message": "Note not found."}, 404
