#!/usr/bin/env python
#coding=utf-8

from flask import render_template, redirect, request, \
			 url_for, flash,abort,make_response,current_app
from . import main
from .. import db
from ..models import User,Role,Post,Permission,Comment
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from flask.ext.login import login_required,current_user
from flask.ext.sqlalchemy import get_debug_queries
from ..decorators import admin_required,permission_required


@main.route('/',methods=["GET","POST"])
def index():
    	form = PostForm()
	if form.validate_on_submit() and \
			current_user.can(Permission.WRITE_ARTICLES):
		post = Post(body=form.body.data,
				author=current_user._get_current_object())
		db.session.add(post)
		db.session.commit()
		return redirect(url_for(".index"))
	page = request.args.get("page",1,type=int)
	offset = request.args.get("offset",5,int)
	#在首页中显示所关注用户文章
	show_follower = False
	if current_user.is_authenticated:
		show_follower = bool(request.cookies.get('show_follower',''))
	if show_follower:
		query = current_user.follow_posts
	else:
		query = Post.query
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=offset, error_out=False)
	posts = pagination.items
	return render_template("index.html",form=form,posts=posts,pagination=pagination,
							show_follower=show_follower)


@main.route('/post/<int:id>',methods=["GET","POST"])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	'''
	评论的 author
	字段也不能直接设为 current_user ,因为这个变量是上下文代理对象。真正的 User 对象要
	使用表达式 current_user._get_current_object() 获取。
	'''
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
					post=post,
					author=current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		return redirect(url_for('.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	offset = request.args.get("offset",3,int)
	if page == -1:
		page = (post.comments.count() -1)/offset + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
			page, per_page=offset,
			error_out=False)
	comments = pagination.items
	'''comments用于显示评论, pagination用于分页'''
	return render_template('post.html', posts=[post], form=form,
				comments=comments, pagination=pagination)


@main.route('/moderate',methods=["GET","POST"])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page',1,type=int)
	offset = request.args.get("offset",5,int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page,offset,error_out=False)
	comments = pagination.items
	return render_template('moderate.html',comments=comments,
		pagination=pagination,page=page)


@main.route('/moderate/enable/<int:id>',methods=["GET","POST"])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	page = request.args.get('page',1,type=int)
	return redirect(url_for('.moderate',page=page))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()
	page=request.args.get('page', 1, type=int)
	return redirect(url_for('.moderate',page=page))

@main.route("/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and \
			not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		db.session.commit()
		flash('The post has been updated.')
		return redirect(url_for('.post',id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html',form=form)


@main.route("/user/<username>")
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	posts = user.posts.order_by(Post.timestamp.desc()).all()
	return render_template("user.html",user=user,posts=posts)


@main.route('/follow/<username>',methods=["GET","POST"])
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	flash('You are now following % s.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>',methods=["GET","POST"])
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash("You are haven't followed this user.")
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash('You are now unfollow % s.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/fans/<username>',methods=["GET","POST"])
def fans(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type=int)
	offset = request.args.get("offset",10,type=int)
	pagination = user.fans.paginate(page,per_page=offset,error_out=False)
	follows = [{'user':item.fan,'timestamp':item.timestamp}
				for item in pagination.items]
	return render_template('follower.html', user=user, title="Fans of",
							endpoint='.fans', pagination=pagination,
							follows=follows)


@main.route('/followers/<username>',methods=["GET","POST"])
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type=int)
	offset = request.args.get("offset",10,type=int)
	pagination = user.followers.paginate(page,per_page=offset,error_out=False)
	follows = [{'user':item.follower,'timestamp':item.timestamp}
				for item in pagination.items]
	return render_template('follower.html', user=user, title="Followers of",
							endpoint='.followers', pagination=pagination,
							follows=follows)


@main.route("/all",methods=["GET","POST"])
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_follower','',max_age=30*24*60*60)
	return resp


@main.route("/follower",methods=["GET","POST"])
@login_required
def show_follower():
	#设置cookie
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_follower','1',max_age=30*24*60*60)
	return resp


@main.route("/edit-profile",methods=["GET","POST"])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.self_introduction = form.self_introduction.data
		db.session.add(current_user)
		db.session.commit()
		flash("Your profile has been updated.")
		return redirect(url_for(".user",username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.self_introduction.data = current_user.self_introduction
	return render_template("edit_profile.html",form=form)


@main.route("/edit-profile/<int:id>",methods=["GET","POST"])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.self_introduction = form.self_introduction.data
		db.session.add(user)
		db.session.commit()
		flash('The profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.self_introduction.data = user.self_introduction
	return render_template('edit_profile.html', form=form, user=user)


@main.after_app_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= current_app.config['FLASKY_DB_QUERY_TIME_THRESHOLD']:
			current_app.logger.warning(
				'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
					(query.statement, query.parameters, query.duration, query.context))
	return response


@main.route('/shutdown')
def server_shutdown():
	if not current_app.testing:
		abort(404)
	shutdown = request.environ.get('werkzeug.server.shutdown')
	if not shutdown:
		abort(500)
	shutdown()
	return 'Shutting down...'


	

