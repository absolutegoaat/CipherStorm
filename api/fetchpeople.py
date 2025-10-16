from flask import Blueprint, jsonify
from database import DatabaseManager
from api.auth import require_api_key # makes auth for the API

people_bp = Blueprint("people", __name__)

@people_bp.route("/api/people", methods=["GET"])
@require_api_key
def get_people():
    db = DatabaseManager()
    people = db.get_all_people()
    
    return jsonify(people)