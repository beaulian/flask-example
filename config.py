import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
	SQLALSHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = "smtp.qq.com"
	MAIL_PORT = 25
	MAIL_USE_TLS = False
	MAIL_USE_SSL = False
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	FLASK_MAIL_SUBJECT_PREFIX = "[Flask]"
	FLASK_MAIL_SENDER = os.environ.get("FLASK_MAIL_SENDER")
	FLASK_ADMIN = os.environ.get("FLASK_ADMIN")

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALSHEMY_DATABASE_URL = os.environ.get("DEV_DATABASE_URL") or \
		"sqlite:///" + os.path.join(basedir,"data-dev.sqlite")


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
	"development":DevelopmentConfig,
	"testing":TestingConfig,
	"production":ProductionConfig,
	"default":DevelopmentConfig
}

