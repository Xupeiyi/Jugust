import unittest
from app import create_app, db
from app.models import Role

class ModelTest(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()