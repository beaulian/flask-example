#!/usr/bin/env python
#coding=utf-8

from flask import jsonify,g,request
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import login_required, current_user
from ..models import AnonymousUser,User
from .errors import unauthorized,forbidden
from . import api
from .. import db
from ..auth import auth


auth = HTTPBasicAuth()
'''
现在,API 蓝本中的所有路由都能进行自动认证。
而且作为附加认证, before_request 处
理程序还会拒绝已通过认证但没有确认账户的用户。
'''
@api.before_request
@auth.login_required
def before_request():
	if not g.current_user.is_anonymous and \
			not g.current_user.confirmed:
		return forbidden('Unconfirmed account')

@auth.verify_password
def verify_password(email_or_token, password):
	if not email_or_token:
		g.current_user = AnonymousUser()
		return True
	if not password:
		g.current_user = User.verify_auth_token(email_or_token)
		g.token_used = True
		return g.current_user is not None
	user = User.query.filter_by(email=email_or_token).first()
	if not user:
		return False
	g.current_user = user
	g.token_used = False
	return user.verify_password(password)

@api.route('/token')
def get_token():
	if g.current_user.is_anonymous() or g.token_used:
		return unauthorized('Invalid credentials')
	return jsonify({'token': g.current_user.generate_auth_token(
		expiration=3600), 'expiration': 3600})

@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')
