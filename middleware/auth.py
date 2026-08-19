from functools import wraps

from flask import request

from services.user import user_exists
from utils.jwt_manager import decode_access_token


def require_auth(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header is None:
            return {"message": "Missing Authorization header"}, 401
        if not auth_header.startswith("Bearer "):
            return {
                "message": "Invalid Authorization format. Must be 'Bearer <token>'"
            }, 401

        token = auth_header.removeprefix("Bearer ")
        if not token or token.isspace():
            return {"message": "Token is missing."}, 401

        payload = decode_access_token(token)
        message = payload.get("message")
        if message != "done":
            return {"message": f"{message} token."}, 401
        token_type = payload.get("type")
        if token_type != "access":
            return {"message": "Invalid token type. Access token required."}, 401
        user_id = payload.get("user_id")
        if user_id is None :
            return {"message": "Invalid token."}, 401
        if not user_exists(user_id) :
            return {"message": "User no longer exists in the system."}, 401
        kwargs["user_id"] = user_id
        return func(*args, **kwargs)

    return decorated_function
