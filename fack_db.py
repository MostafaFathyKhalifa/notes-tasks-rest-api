import json

try:
    with open("fack_db.json", "r") as f:
        db = json.load(f)
except FileNotFoundError:
    with open("fack_db.json", "w") as f:
        db = {"notes": []}
        json.dump(db, f)