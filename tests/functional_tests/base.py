import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db, mail, fake
from app.models import Role, User, Post



class FunctionalTest(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(cls):
		#打开Chrome
		options = webdriver.ChromeOptions()
		#options.add_argument('headless')
		options.add_argument('--no-sandbox')
		try:
			cls.client = webdriver.Chrome(options=options)
		except:
			pass

		#浏览器不能打开就跳过
		if cls.client:
			#create the application
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			#关闭日志，使输出简洁
			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLevel('ERROR')

			#数据库输入少量虚拟数据
			db.create_all()
			Role.insert_roles()
			fake.users(10)
			fake.posts(10)

			#添加管理员john(已确认)
			admin_role = Role.query.filter_by(permissions=0xff).first()
			admin = User(email='john@example.com',
								   username='john', password='cat',
								   role=admin_role, confirmed=True)
			db.session.add(admin)
			db.session.commit()

			#添加普通用户ken(已确认)
			user = User(email='ken@example.com',
								 username='ken', password='rat',
								 confirmed=True)
			db.session.add(user)
			db.session.commit()

			#另一个线程中启动服务器
			cls.server_thread = threading.Thread(target=cls.app.run, 
																				 kwargs={'debug': False})
			cls.server_thread.start()

			time.sleep(1)


	@classmethod
	def tearDownClass(cls):
		if cls.client:
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.quit()
			cls.server_thread.join()

			#销毁数据库
			db.session.remove()
			db.drop_all()
			

			#销毁上下文
			cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('浏览器不可用')

	def tearDown(self):
		pass

	def login_john(self):
		self.client.get('http://localhost:5000/auth/login')
		self.client.find_element_by_name('email').send_keys('john@example.com')
		self.client.find_element_by_name('password').send_keys('cat')
		self.client.find_element_by_name('submit').click()

	def login_ken(self):
		self.client.get('http://localhost:5000/auth/login')
		self.client.find_element_by_name('email').send_keys('ken@example.com')
		self.client.find_element_by_name('password').send_keys('rat')
		self.client.find_element_by_name('submit').click()