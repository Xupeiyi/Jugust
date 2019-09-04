import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
	MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TILS', 'true').lower() in \
		['true', 'on', '1']
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	JUGUST_MAIL_SUBJECT_PREFIX = '[Jugust]'
	JUGUST_MAIL_SENDER = 'Jugust Admin <957681460@qq.com>'
	JUGUST_ADMIN = os.environ.get('JUGUST_ADMIN')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	JUGUST_POSTS_PER_PAGE = 10
	JUGUST_FOLLOWERS_PER_PAGE = 20
	JUGUST_COMMENTS_PER_PAGE = 10
	JUGUST_NOTIFICATION_PER_PAGE = 20

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite://'
	WTF_CSRF_ENABLED = False
	WTF_CSRF_CHECK_DEFAULT  = False


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABSE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,

	'default': DevelopmentConfig
} 
