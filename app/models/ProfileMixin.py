from datetime import datetime
from .. import db
class ProfileMixin(db.Model):
	__abstract__ = True

	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen =  db.Column(db.DateTime(), default=datetime.utcnow)

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)