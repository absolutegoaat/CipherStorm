from flask import Blueprint, jsonify
from database import DatabaseManager
from api.auth import require_api_key # makes auth for the API

people_bp = Blueprint("people", __name__)
db = DatabaseManager()

# TODO: Validation Route

@people_bp.route("/api/people", methods=["GET"])
@require_api_key
def get_people():
    people = db.get_all_people()
    
    return jsonify(people)

@people_bp.route("/api/people/<int:person_id>")
@require_api_key
def get_person(person_id):
    person = db.get_person(person_id=person)

    if person:
        return jsonify(person)
    else
        return jsonify({
            'message': 'Person is not found in database.'
        }), 404