#!/usr/bin/env python
#coding=utf-8

from functools import wraps
from flask import abort,g
from ..models import Permission
from flask.ext.login import current_user

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kwargs):
			'''
			这里的g很重要,不然用httpie时会报没有权限的错误
			因为http协议是无状态的协议,一般来讲,在浏览器中
			的请求,因为浏览器 会以cookie的方式记住客户端的
			信息,但是web浏览器之外的客户端很难提供对cookie
			的支持,所以flask用g来保存当前用户的信息
			'''
			if not g.current_user.can(permission):  
				abort(403)
			return f(*args,**kwargs)
		return decorated_function
	return decorator
