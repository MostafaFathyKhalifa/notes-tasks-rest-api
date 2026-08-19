import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

# =====================
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"  # Algorithm used for encoding and decoding the JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes
REFRESH_TOKEN_EXPIRE_MINUTES = (
    60 * 24 * 7
)  # Refresh token expiration time in minutes (7 days)


# =============================================
def create_access_token(user_id: int) -> str:
    """
    Creates a JWT access token for the given user ID.

    Args:
        user_id (int): The user ID for which to create the token.
    """
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expire_time,
        "type": "access",
        "auth_level": 1,
        "refresh_count": 0,
        "fresh": True,
    }

    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """
    Decodes a JWT access token and returns the payload.

    Args:
        token (str): The JWT access token to decode.
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp"]},
        )
        user_id = payload.get("sub")
        fresh = payload.get("fresh")
        type = payload.get("type")
        refresh_count = payload.get("refresh_count")
        auth_level = payload.get("auth_level")
        user_id  = str(user_id)
        if not user_id.strip() or not user_id.isdigit():
            return {"message": "invalid"}
        user_id = int(user_id)
        return {
            "user_id": user_id,
            "fresh": fresh,
            "type": type,
            "refresh_count": refresh_count,
            "auth_level": auth_level,
            "message": "done",
        }
    except jwt.ExpiredSignatureError:
        return {"message": "expired"}
    except jwt.InvalidTokenError:
        return {"message": "invalid"}


def create_refresh_token(token: str) -> str | None:
    decode_result = decode_access_token(token)
    if decode_result["message"] != "done":
        return None  # Return None if the token is invalid or expired

    refresh_count = decode_result.get("refresh_count")

    if refresh_count is None or refresh_count >= 10:
        return None  # Return None if the refresh count exceeds the limit

    user_id = decode_result["user_id"]
    type = decode_result.get("type")
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )

    if type in ("old_refresh", "refresh"):
        refresh_count += 1

    payload = {
        "sub": user_id,
        "exp": expire_time,
        "type": "refresh" if type == "access" else "old_refresh",
        "auth_level": 2 if type == "access" else 3,
        "refresh_count": refresh_count,
        "fresh": False,
    }

    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token
