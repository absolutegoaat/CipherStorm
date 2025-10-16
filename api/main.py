from flask import Blueprint, jsonify
from database import DatabaseManager
from api.auth import require_api_key # makes auth for the API
from api.auth import require_administrator

api = Blueprint("people", __name__)
db = DatabaseManager()

@api.route("/api/token_validate", methods=['GET'])
@require_api_key
def validate():
    return jsonify({
        'message': 'API Token is valid'
    }), 200

@api.route("/api/users", methods=["GET"])
@require_api_key
@require_administrator
def get_users():
    users = db.get_all_users()
    return jsonify(users)

@api.route("/api/people", methods=["GET"])
@require_api_key
def get_people():
    people = db.get_all_people()
    return jsonify(people)

@api.route("/api/people/<int:person_id>")
@require_api_key
def get_person(person_id):
    person = db.get_person(person_id=person)

    if person:
        return jsonify(person)
    else:
        return jsonify({
            'message': 'Person is not found in database.'
        }), 404