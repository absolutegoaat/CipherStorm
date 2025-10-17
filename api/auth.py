from functools import wraps
from flask import request, jsonify
from database import DatabaseManager

db = DatabaseManager()

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return jsonify({"message": "API key missing"}), 401
        
        if not db.validate_api_key(api_key):
            return jsonify({"message": "Invalid API key"}), 403
        else:
            return f(*args, **kwargs)
        
    return decorated

def require_administrator(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        
        if db.validate_api_administration(api_key) == 0:
            return jsonify({"message": "Authorized 403"})
        else:
            return f(*args, **kwargs)
        
    return decorated   