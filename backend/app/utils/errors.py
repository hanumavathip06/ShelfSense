from flask import jsonify

def api_error(message, code=400):
    return jsonify({"error": {"code": code, "message": message}}), code
