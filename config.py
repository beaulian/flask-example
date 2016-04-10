#coding=utf-8
import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
	SQLALSHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = "smtp.163.com"
	#MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USE_SSL = False
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	FLASK_MAIL_SUBJECT_PREFIX = "[Flask]"
	FLASK_MAIL_SENDER = os.environ.get("FLASK_MAIL_SENDER")
	FLASK_ADMIN = os.environ.get("FLASK_ADMIN")
	#SERVER_NAME = "127.0.0.1:5000"
	#启用缓慢查询记录功能
	SQLALCHEMY_RECORD_QUERIES = True  #告诉 Flask-SQLAlchemy 启用记录查询统计数字的功能
	FLASKY_DB_QUERY_TIME_THRESHOLD = 0.5     #缓慢查询的阈值设为0.5秒

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
		"sqlite:///" + os.path.join(basedir,"data-dev.sqlite")


class TestingConfig(Config):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class ProductionConfig(Config):
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)

		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None
		if getattr(cls,'MAIL_USERNAME', None) is not None:
			credentials = (cls,MAIL_USERNAME, cls.MAIL_PASSWORD)
			if getattr(cls, 'MAIL_USE_TLS', None):
				secure = ()
		mail_handler = SMTPHandler(
			mailhost = cls.FLASK_MAIL_SENDER,
			toaddrs=[cls.FLASK_ADMIN],
			subject=cls.FLASK_MAIL_SUBJECT_PREFIX+' Application Error',
			credentials=credentials, #证书
			secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)


config = {
	"development":DevelopmentConfig,
	"testing":TestingConfig,
	"production":ProductionConfig,
	"default":DevelopmentConfig
}

