from datetime import datetime
from .. import db
from sqlalchemy.ext.declarative import declared_attr

class Collect(db.Model):
	collector_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
											primary_key=True)
	collected_id = db.Column(db.Integer, db.ForeignKey('posts.id'), 
											primary_key=True)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	collector = db.relationship('User', back_populates='collections', lazy='joined')
	collected = db.relationship('Post', back_populates='collectors', lazy='joined')


class CollectMixin(db.Model):
	__abstract__ = True

	@declared_attr
	def collections(cls):
		return db.relationship('Collect', back_populates='collector', cascade='all')

	@property
	def collected_posts(self):
		from . import Post
		return Post.query.join(Collect, Collect.collected_id == Post.id)\
			.filter(Collect.collector_id == self.id)
	
	def is_collecting(self, post):
		return Collect.query.with_parent(self).filter_by(
			collected_id=post.id).first() is not None

	def collect(self, post):
		if not self.is_collecting(post):
			collect = Collect(collector=self, collected=post)
			db.session.add(collect)
			db.session.commit()

	def uncollect(self, post):
		collect = Collect.query.with_parent(self).\
									filter_by(collected_id=post.id).first()
		if collect:
			db.session.delete(collect)
			db.session.commit()