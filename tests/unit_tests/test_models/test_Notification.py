from datetime import datetime
from .base import ModelTest
from app import db
from app.models import User, Notification

def u1_get_n1():
	u1 = User(email='john@example.com', password='cat')
	n1 = Notification(message='a message', receiver=u1)
	db.session.add(u1)
	db.session.add(n1)
	db.session.commit()
	return u1, n1

class NotificationModelTest(ModelTest):

	def test_Notification_timestamp_is_correct(self):
		timestamp_before = datetime.utcnow()
		u1, n1 = u1_get_n1()
		timestamp_after = datetime.utcnow()
		self.assertTrue(timestamp_before <= n1.timestamp <= timestamp_after)

	def test_notifications_count(self):
		u1, n1 = u1_get_n1()
		self.assertEqual(u1.notifications.__len__(), 1)

	def test_Notification_not_exist_after_user_deleted(self):
		u1, n1 = u1_get_n1()
		db.session.delete(u1)
		db.session.commit()
		self.assertEqual(Notification.query.count(), 0)

