from flask import jsonify
from werkzeug.exceptions import HTTPException
from app import app
import traceback

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    
    if isinstance(e, HTTPException):
        return jsonify({
            'error': str(e),
            'status_code': e.code
        }), e.code
        
    return jsonify({
        'error': 'Internal Server Error',
        'status_code': 500
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Resource not found',
        'status_code': 404
    }), 404

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        'error': 'Forbidden',
        'status_code': 403
    }), 403