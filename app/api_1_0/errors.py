from flask import request,render_template,jsonify
from app.exceptions import ValidationError
from .. import main
from . import api


def ok(message):
	response = jsonify({'success': 'Ok', 'message': message})
	response.status_code = 200
	return response

def created(message):
	response = jsonify({'success': 'Created', 'message': message})
	response.status_code = 201
	return response

def bad_request(message):
	response = jsonify({'error': 'Bad request', 'message': message})
	response.status_code = 400
	return response

def unauthorized(message):
	response = jsonify({'error': 'Unauthorized', 'message': message})
	response.status_code = 401
	return response

def forbidden(message):
	response = jsonify({'error': 'Forbidden', 'message': message})
	response.status_code = 403
	return response

def method_not_allowed(message):
	response = jsonify({'error': 'Method not allowed', 'message': message})
	response.status_code = 405
	return response


@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])