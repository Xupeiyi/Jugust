import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db, fake
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(cls):
		#start Chrome
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		options.add_argument('--no-sandbox')
		try:
			cls.client = webdriver.Chrome(options=options)
		except:
			pass

		#skip these tests if the browser could not be started
		if cls.client:
			#create the application
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			#suppress logging to keep unittest output clean
			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLevel('ERROR')

			#create the database and populate with some fake data
			db.create_all()
			Role.insert_roles()
			fake.users(10)
			fake.posts(10)

			#add an admin user
			admin_role = Role.query.filter_by(permissions=0xff).first()
			admin = User(email='john@example.com',
								   username='john', password='cat',
								   role=admin_role, confirmed=True)
			db.session.add(admin)
			db.session.commit()

			#start the Flask server in a thread
			cls.server_thread = threading.Thread(target=cls.app.run, 
																				 kwargs={'debug': False})
			cls.server_thread.start()

			#give the server a second to ensure it is up


	@classmethod
	def tearDownClass(cls):
		if cls.client:
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.quit()
			cls.server_thread.join()

			#destroy database
			db.drop_all()
			db.session.remove()

			#remove application context
			cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('浏览器不可用')

	def tearDown(self):
		pass


	def test_admin_home_page(self):
		#进入首页
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('登录', self.client.page_source))

		#进入登录页面
		self.client.find_element_by_link_text('登录').click()
		self.assertIn('<h1>登录</h1>', self.client.page_source)

		#登录
		self.client.find_element_by_name('email').send_keys('john@example.com')
		self.client.find_element_by_name('password').send_keys('cat')
		self.client.find_element_by_name('submit').click()
		
		time.sleep(2)


		self.assertTrue(re.search('退出', self.client.page_source))

		#进入用户档案页面
		self.client.find_element_by_link_text('档案').click()
		self.assertIn('john', self.client.page_source.replace('\n',''))