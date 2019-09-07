from .base import ModelTest
from app import db
from app.models import User


class UserModelTest(ModelTest):

	def test_timestamp(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		self.assertTrue(
			(datetime.utcnow() - u.member_since).total_seconds() < 3)
		self.assertTrue(
			(datetime.utcnow() - u.last_seen).total_seconds() < 3)	

	def test_ping(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		time.sleep(2)
		last_seen_before = u.last_seen
		u.ping()
		self.assertTrue(u.last_seen > last_seen_before)

	def test_gravatar(self):
		u = User(email='john@example.com', password='cat')
		with self.app.test_request_context('/'):
			gravatar = u.gravatar()
			gravatar_256 = u.gravatar(size=256)
			gravatar_pg = u.gravatar(rating='pg')
			gravatar_retro = u.gravatar(default='retro')
		self.assertTrue('https://secure.gravatar.com/avatar/' + 
									  'd4c74594d841139328695756648b6bd6' in gravatar)
		self.assertTrue('s=256' in gravatar_256)
		self.assertTrue('r=pg' in gravatar_pg)
		self.assertTrue('d=retro' in gravatar_retro)

	