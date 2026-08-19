import os
import traceback

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from database import db
from routers import note_blp, user_blp
from utils.datetime_utils import get_datetime_now
# === App Setup ===
app = Flask(__name__)
CORS(app)  # السماح بالوصول من أي مصدر (Cross-Origin Resource Sharing
URL_PREFIX = "/api/v1"
load_dotenv()
# =========================
# == App Configuration ==
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_SQLITE")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# === Flask-Smorest Configuration
app.config["API_TITLE"] = "Notes and TaskManagers API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
# =========================
#=== Errror Handler ====
@app.errorhandler(Exception)
def handel_global_error(error):
    print(f"Unhandled Exception: {error}")
    with open("error.txt" ,"a") as f:
        f.write("=" * 50 + "\n")
        f.write(f"Time: {get_datetime_now()}\n")
        f.write(f"Error Type: {type(error).__name__}\n")
        f.write(f"Error Message: {error!r}\n")
        f.write("-" * 50 + "\n")
        f.write(traceback.format_exc())
        f.write("\n\n")
    return {"message": "An unexpected internal error occurred. Please try again later."}, 500
# === Initialize Database and API ===
db.init_app(app)
api = Api(app)
# ==========================
# == Create Database Tables ==
with app.app_context():
    db.create_all()
# =========================
# == Register Blueprints ==
api.register_blueprint(note_blp)
api.register_blueprint(user_blp)


# == Helper Functions ==
def url_prefix(endpoint: str = "") -> str:
    return f"{URL_PREFIX}{endpoint}"


# ========================
# === EndPoints ===
@app.get(url_prefix("/"))
def index():
    return {"message": "Welcome to the API!"}, 200


@app.get(url_prefix("/health"))
def health():
    return {"status": "ok"}, 200
