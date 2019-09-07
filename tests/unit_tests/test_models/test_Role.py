from .base import ModelTest
from app import db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTest(ModelTest):

	def test_user_role(self):
		u = User(email='john@example.com', password='cat')
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertFalse(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))

	def test_moderator_role(self):
		r = Role.query.filter_by(name='Moderator').first()
		u = User(email='john@example.com', password='cat', role=r)
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertTrue(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))

	def test_administrator_role(self):
		r = Role.query.filter_by(name='Administrator').first()
		u = User(email='john@example.com', password='cat', role=r)
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE))
		self.assertTrue(u.can(Permission.MODERATE))
		self.assertTrue(u.can(Permission.ADMIN))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))
		self.assertFalse(u.can(Permission.COMMENT))
		self.assertFalse(u.can(Permission.WRITE))
		self.assertFalse(u.can(Permission.MODERATE))
		self.assertFalse(u.can(Permission.ADMIN))