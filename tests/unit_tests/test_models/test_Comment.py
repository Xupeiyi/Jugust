from datetime import datetime
from .base import ModelTest
from app import db
from app.models import User, Post, Comment


def u1_comments_p1():
	u1 = User(email='john@example.com', password='cat')
	p1 = Post(title='title', body='*some*body')
	c1 = Comment(body='*other*body', post=p1, author=u1)
	db.session.add(u1)
	db.session.add(p1)
	db.session.add(c1)
	db.session.commit()
	return u1, c1, p1

class CommentModelTest(ModelTest):

	def test_Comment_has_body_html_after_created(self):
		u1, c1, p1 = u1_comments_p1()
		self.assertTrue(c1.body_html is not None)

	def test_Post_body_html_changed_after_body_changed(self):
		u1, c1, p1 = u1_comments_p1()
		body_html_before = c1.body_html
		c1.body = '*another*body'
		db.session.add(c1)
		db.session.commit()
		body_html_after = c1.body_html
		self.assertNotEqual(body_html_before, body_html_after)

	def test_user_has_Comment(self):
		u1, c1, p1 = u1_comments_p1()
		self.assertTrue(u1.comments.count() == 1)
		c = u1.comments.all()[-1]
		self.assertTrue(c is c1)

	def test_post_has_comment(self):
		u1, c1, p1 = u1_comments_p1()
		self.assertTrue(p1.comments.count() == 1)
		c = p1.comments.all()[-1]
		self.assertTrue(c is c1)

	def test_Comment_timestamp_is_correct(self):
		timestamp_before = datetime.utcnow()
		u1, c1, p1 = u1_comments_p1()
		timestamp_after = datetime.utcnow()
		self.assertTrue(timestamp_before <= c1.timestamp <= timestamp_after)

	def test_Comment_not_exist_after_post_deleted(self):
		u1, c1, p1 = u1_comments_p1()
		db.session.delete(p1)
		db.session.commit()
		self.assertEqual(Comment.query.count() ,0)

	def test_Comment_not_disabled_when_created(self):
		u1, c1, p1 = u1_comments_p1()
		self.assertEqual(c1.disabled, False) 
