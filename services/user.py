# services/user.py
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db
from models import UserModel
from utils.hashing import hash_password, verify_password
from utils.jwt_manager import create_access_token


def register_user(user_data: dict):
    user_name = user_data.get("user_name")
    email = user_data.get("email")
    password = user_data.get("password")

    if not user_name or not email or not password:
        return None, "All fields (user_name, email, password) are required."
    if not isinstance(user_name, str) or len(user_name) < 5:
        return None, "User name must string and be at least 5 characters."
    if not isinstance(email, str) or "@" not in email or "." not in email:
        return None, "Invalid email format."
    if not isinstance(password,str):
        return None,"Invalid Password, must be string"

    if UserModel.query.filter_by(user_name=user_name).first():
        return None, "Username already exists."

    if UserModel.query.filter_by(email=email).first():
        return None, "Email already exists."

    password_hash = hash_password(password)

    new_user = UserModel()
    new_user.user_name = user_name
    new_user.email = email
    new_user.password_hash = password_hash

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, "User name or email already exists."
    except SQLAlchemyError:
        db.session.rollback()
        return None, "An error occurred during registration."

    token = create_access_token(new_user.id)
    return {
        "id": new_user.id,
        "user_name": new_user.user_name,
        "email": new_user.email,
        "access_token": token,
    }, "User registered successfully."


def login_user(user_data: dict):
    email = user_data.get("email")
    password = user_data.get("password")

    if not email or not password:
        return None, "Email and password are required."

    if email and not isinstance(email, str):
        return None, "email must be string."
    if password and not isinstance(password, str):
        return None, "password must be string."

    user: UserModel | None = UserModel.query.filter_by(email=email.strip()).first()

    if user is None:
        return None, "Invalid email or password."

    if not verify_password(user.password_hash, password):
        return None, "Invalid email or password."

    token = create_access_token(user.id)
    return {
        "id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "access_token": token,
    }, "Login successful."


def user_exists(user_id: int) -> bool:
    user = UserModel.query.get(user_id)
    return user is not None
