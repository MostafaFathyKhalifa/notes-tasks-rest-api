from flask import request
from flask_smorest import Blueprint

import services.user as user_service

# =====================
# == Blueprint Setup ==
# =====================
user_blp = Blueprint(
    name="user",
    import_name=__name__,
    description="User Registration and Login",
    url_prefix="/api/v1/users",
)


# ======================================
# ============== Routes ================
# ======================================
@user_blp.post("/register")
def register():
    user_data = request.get_json()
    if not isinstance(user_data, dict):
        return {"message": "Request body must be a JSON object."}, 400

    if not user_data:
        return {"message": "Request body must be JSON."}, 400
    user_data, message = user_service.register_user(user_data)
    if user_data is None:
        if "required" in message or "format" in message or "characters" in message or "Invalid" in message:
            status_code = 400

        elif "exists" in message:
            status_code = 409

        else:
            status_code = 500

        return {"message": message}, status_code
    return {"user": user_data, "message": message}, 201


@user_blp.post("/login")
def login():
    user_data_request = request.get_json()
    if not isinstance(user_data_request, dict):
        return {"message": "Request body must be a JSON object."}, 400
    if not user_data_request:
        return {"message": "Request body must be JSON."}, 400
    user_data, message = user_service.login_user(user_data_request)
    if user_data is None:
        if any(word in message for word in ["required", "must be"]):
            status_code = 400
        elif "Invalid" in message:
            status_code = 401
        else:
            status_code = 500
        return {"message": message}, status_code
    return {
        "user": {
            "id": user_data["id"],
            "user_name": user_data["user_name"],
            "email": user_data["email"],
        },
        "access_token": user_data["access_token"],
        "message": message,
    }, 200
