from datetime import datetime
from .. import db
from sqlalchemy.ext.declarative import declared_attr


class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
									 primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
									 primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class FollowMixin(db.Model):

	__abstract__ = True
	#users followed by current user
	@declared_attr
	def followed(cls):
		return db.relationship('Follow',
									 foreign_keys=[Follow.follower_id],
									 backref=db.backref('follower', lazy='joined'),
									 lazy='dynamic',
									 cascade='all, delete-orphan')
	
	#users following current user
	@declared_attr
	def followers(cls):
		return db.relationship('Follow',
									  foreign_keys=[Follow.followed_id],
									  backref=db.backref('followed', lazy='joined'),
									  lazy='dynamic',
									  cascade='all, delete-orphan')

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)
			db.session.commit()

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
			db.session.commit()
			
	def is_following(self, user):
		if user.id is None:
			return False
		return self.followed.filter_by(
			followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		if user.id is None:
			return False
		return self.followers.filter_by(
			follower_id=user.id).first() is not None

	@property
	def followed_posts(self):
		from . import Post
		return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
			 .filter(Follow.follower_id == self.id)
