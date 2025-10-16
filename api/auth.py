from functools import wraps
from flask import request, jsonify
from database import DatabaseManager

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return jsonify({"message": "API key missing"}), 401

        db = DatabaseManager()
        
        if not db.validate_api_key(api_key):
            return jsonify({"message": "Invalid API key"}), 403
        else:
            return f(*args, **kwargs)
        
    return decorated
