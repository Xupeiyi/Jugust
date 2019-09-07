from datetime import datetime
from .base import ModelTest
from app import db
from app.models import User, Post


def u1_creates_p1():
	u1 = User(email='john@example.com', password='cat')
	p1 = Post(title='title', body='*some*body', author=u1)
	db.session.add(u1)
	db.session.add(p1)
	db.session.commit(c1)
	return u1, p1

class PostModelTest(ModelTest):

	def test_Post_has_body_html_after_created(self):
		u1, p1 = u1_creates_p1()
		self.assertTrue(p1.body_html is not None)

	def test_Post_body_html_changed_after_body_changed(self):
		u1, p1 = u1_creates_p1()
		body_html_before = p1.body_html
		p1.body = '*another*body'
		db.session.add(p1)
		db.session.commit()
		body_html_after = p1.body_html
		self.assertNotEqual(body_html_before, body_html_after)

	def test_user_has_Post(self):
		u1, p1 = u1_creates_p1()
		self.assertTrue(u1.posts.count() == 1)
		p = u1.posts.all()[-1]
		self.assertTrue(p is p1)

	def test_Post_timestamp_is_correct(self):
		timestamp_before = datetime.utcnow()
		u1, p1 = u1_creates_p1()
		timestamp_after = datetime.utcnow()
		self.assertTrue(timestamp_before <= p1.timestamp <= timestamp_after)

