from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin

from .. import db,login_manager, whooshee
from .AuthMixin import AuthMixin
from .FollowMixin import Follow, FollowMixin
from .CollectMixin import Collect, CollectMixin
from .ProfileMixin import ProfileMixin
from .Role import Permission, Role


@whooshee.register_model('username', 'name')
class User(UserMixin, AuthMixin, FollowMixin, CollectMixin, ProfileMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	avatar_hash = db.Column(db.String(32))
	
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')
	notifications = db.relationship('Notification', back_populates='receiver', cascade='all')

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if (self.email == current_app.config['JUGUST_ADMIN']):
				self.role = Role.query.filter_by(name='Administrator').first()
			if (self.role is None):
				self.role = Role.query.filter_by(default=True).first()
		if (self.email is not None and self.avatar_hash is None):
			self.avatar_hash = self.gravatar_hash()
		self.follow(self)

	def can(self, perm):
		return self.role is not None and self.role.has_permission(perm)

	def is_administrator(self):
		return self.can(Permission.ADMIN)

	def gravatar_hash(self):
		return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

	def gravatar(self, size=100, default='identicon', rating='g'):
		url = 'https://secure.gravatar.com/avatar'
		hash = self.avatar_hash or self.gravatar_hash()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)
	
	def __repr__(self):
		return '<User %r>' %self.username
	

class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



@whooshee.register_model('title', 'body')
class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='post', lazy='dynamic')
	collectors = db.relationship('Collect', back_populates='collected', cascade='all')

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
							'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
							'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
			 markdown(value, output_format='html'),
			 tags=allowed_tags, strip=True))

	def is_collected_by(self, user):
		if user.id is None:
			return False
		return Collect.query.with_parent(self).filter_by(
			collector_id=user.id).first() is not None

db.event.listen(Post.body, 'set', Post.on_changed_body)
	

class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
							'strong']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Notification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.Text)
	is_read = db.Column(db.Boolean, default=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	receiver = db.relationship('User', back_populates='notifications')
