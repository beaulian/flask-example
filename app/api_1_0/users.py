#!/usr/bin/env python
#coding=utf-8

from flask import jsonify, request, url_for,request,url_for
from . import api
from ..models import User, Post


@api.route('/users/<int:id>', methods=["GET"])
def get_user(id):
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())

@api.route('/users/<int:id>/posts/', methods=["GET"])
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    offset = request.args.get('offset', 5, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=offset,
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/follows/',methods=["GET"])
def get_user_follows(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    offset = request.args.get('offset', 5, type=int)
    pagination = user.follow_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=offset,error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'follow_posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


