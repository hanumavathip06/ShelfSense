from flask import Blueprint, jsonify
from sqlalchemy import text
from app.extensions import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        # Ping the database
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        return jsonify({"status": "error", "db": db_status}), 500

    return jsonify({"status": "ok", "db": db_status}), 200
