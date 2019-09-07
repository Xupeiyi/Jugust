from datetime import datetime
from .base import ModelTest
from app import db
from app.models import User, Post, Collect

def create_u1_p1():
	u1 = User(email='john@example.com', password='cat')
	p1 = Post(title='title1', body='body1')
	db.session.add(u1)
	db.session.add(p1)
	db.session.commit()
	return u1, p1


class CollectModelTest(ModelTest):

	def test_collect_not_self_created(self):
		u1, p1 = create_u1_p1()
		self.assertFalse(u1.is_collecting(p1))
		self.assertFalse(p1.is_collected_by(u1))

	def test_is_collecting_and_is_collected_by(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		self.assertTrue(u1.is_collecting(p1))
		self.assertTrue(p1.is_collected_by(u1))

	def test_collect_timestamp_is_correct(self):
		u1, p1 = create_u1_p1()
		timestamp_before = datetime.utcnow()
		u1.collect(p1)
		timestamp_after = datetime.utcnow()
		c = Collect.query.filter_by(collector=u1, collected=p1).first()
		self.assertTrue(timestamp_before <= c.timestamp <= timestamp_after)

	def test_collections_and_collectors_count(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		self.assertTrue(u1.collections.__len__() == 1)
		self.assertTrue(p1.collectors.__len__() == 1)
		
	def test_Collect_match_collections_and_collectors(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		c = u1.collections[-1]
		self.assertTrue(c.collector == u1)
		c= p1.collectors[-1]
		self.assertTrue(c.collected == p1)

	def test_uncollect_deletes_Collect(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		u1.uncollect(p1)
		self.assertTrue(u1.collections.__len__() == 0)
		self.assertTrue(p1.collectors.__len__() == 0)
		self.assertTrue(Collect.query.count() == 0)
	
	def test_Collect_not_exist_after_collected_post_deleted(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		db.session.delete(p1)
		db.session.commit()
		self.assertTrue(Collect.query.count() == 0)
		self.assertTrue(u1.collections.__len__() == 0)

	def test_Collect_not_exist_after_collector_deleted(self):
		u1, p1 = create_u1_p1()
		u1.collect(p1)
		db.session.delete(u1)
		db.session.commit()
		self.assertTrue(Collect.query.count() == 0)
		self.assertTrue(p1.collectors.__len__() == 0)