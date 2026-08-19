from flask import request
from flask_smorest import Blueprint

import services.note as note_service
from middleware.auth import require_auth

# =====================
# == Blueprint Setup ==
# =====================
note_blp = Blueprint(
    name="note",
    import_name=__name__,
    description="Operation in Notes",
    url_prefix="/api/v1/notes",
)


# ======================================
# ============== Routes ================
# ======================================


# === Create a new note ===
@note_blp.post("/")
@require_auth
def create_note(user_id: int):
    new_note_data = request.get_json()
    if not isinstance(new_note_data, dict):
        return {"message": "Request body must be a JSON object."}, 400

    note_data, message = note_service.create_note(new_note_data, user_id)
    if note_data is None:
        error = message
        if error == "Title is already_exists":
            return {"message": error}, 409
        elif error == "An error occurred creating the store.":
            return {"message": error}, 500
        else:
            return {"message": error}, 400
    return {"note": note_data, "message": message}, 201


# == Get all notes ===
@note_blp.get("/")
@require_auth
def get_all_notes(user_id: int):
    note_data, message = note_service.get_all_notes(user_id)
    if message is not None:
        return {"message": message, "notes": note_data}, 200
    return {"notes": note_data}, 200


# === Get a specific note by ID ===
@note_blp.get("/<int:note_id>")
@require_auth
def get_note_by_id(note_id: int, user_id):
    note_data, message = note_service.get_note_by_id(note_id, user_id)
    if note_data is None:
        return {"message": message}, 404
    return {"note": note_data}, 200


# === Update a specific note by ID ===
@note_blp.put("/<int:note_id>")
@require_auth
def update_note_by_id(note_id: int, user_id: int):
    updated_note_data = request.get_json()
    if not isinstance(updated_note_data, dict):
        return {"message": "Request body must be a JSON object."}, 400

    note_data, message = note_service.update_note_by_id(
        note_id, updated_note_data, user_id
    )
    if note_data is None:
        error = message
        if error == "Note not found.":
            return {"message": error}, 404
        elif error == "Title is already_exists":
            return {"message": error}, 409
        elif error == "An error occurred updating the note.":
            return {"message": error}, 500
        else:
            return {"message": error}, 400
    return {"note": note_data, "message": message}, 200


# === Delete a specific note by ID ===
@note_blp.delete("/<int:note_id>")
@require_auth
def delete_note_by_id(note_id: int, user_id: int):
    note_data, message = note_service.delete_note_by_id(note_id, user_id)
    if note_data is None:
        error = message
        if error == "Note not found.":
            return {"message": error}, 404
        elif error == "An error occurred deleting the note.":
            return {"message": error}, 500
        else:
            return {"message": error}, 400

    return {"message": message}, 200
