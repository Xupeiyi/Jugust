import re
import time
import unittest
from selenium import webdriver
from .base import FunctionalTest


class UserTest(FunctionalTest):
	
	def test_user_page(self):
		#john登录
		self.login_john()
		#john进入用户档案页面,看到了自己的信息（用户名, ）
		self.client.find_element_by_link_text('档案').click()
		self.assertIn('<h2class="account-heading">john</h2>', self.client.page_source.replace('\n','').replace(' ',''))

		#john修改了自己的档案
		self.client.find_element_by_link_text('修改档案').click()
		time.sleep(1)
		self.client.find_element_by_name('name').send_keys('John Smith')
		self.client.find_element_by_name('location').send_keys('Earth')
		self.client.find_element_by_name('about_me').send_keys('I love dogs.')
		self.client.find_element_by_name('submit').click()

		#john的信息出现在了个人主页上
		time.sleep(1)
		self.assertIn('John Smith', self.client.page_source)
		self.assertIn('Earth', self.client.page_source)
		self.assertIn('I love dogs.', self.client.page_source)
	
	
	def test_follow(self):
		self.login_john()

		#john访问了john的主页，john的关注数为0
		self.client.get('http://localhost:5000/users/user/john')
		followings_num = self.client.find_elements_by_class_name('badge-info')[1].text
		self.assertEqual(followings_num, '关注 0')

		#john访问了ken的主页，ken的粉丝数为0
		self.client.get('http://localhost:5000/users/user/ken')
		followers_num = self.client.find_elements_by_class_name('badge-info')[0].text
		self.assertEqual(followers_num, '粉丝 0')

		#john关注了ken
		self.client.find_element_by_id('follow').click()

		#ken的主页上粉丝显示为1
		followers_num = self.client.find_elements_by_class_name('badge-info')[0].text
		self.assertEqual(followers_num, '粉丝 1')
		#john的主页上关注显示为1
		self.client.get('http://localhost:5000/users/user/john')
		followings_num = self.client.find_elements_by_class_name('badge-info')[1].text
		self.assertEqual(followings_num, '关注 1')

		#john的关注页上显示了ken,ken的粉丝页上显示了john
		self.client.get('http://localhost:5000/users/followed_by/john')
		john_followed_by_table = self.client.find_element_by_tag_name('table').text
		self.assertIn('ken', john_followed_by_table)
		self.client.get('http://localhost:5000/users/followers/ken')
		ken_followers_table = self.client.find_element_by_tag_name('table').text
		self.assertIn('john', ken_followers_table)

		#john取关了ken
		self.client.get('http://localhost:5000/users/user/ken')
		self.client.find_element_by_id('unfollow').click()

		#ken的主页上粉丝显示为0
		followers_num = self.client.find_elements_by_class_name('badge-info')[0].text
		self.assertEqual(followers_num, '粉丝 0')
		#john的主页上关注显示为0
		self.client.get('http://localhost:5000/users/user/john')
		followings_num = self.client.find_elements_by_class_name('badge-info')[1].text
		self.assertEqual(followings_num, '关注 0')


		#john的关注页上不显示ken,ken的粉丝页上不显示john
		self.client.get('http://localhost:5000/users/followed_by/john')
		john_followed_by_table = self.client.find_element_by_tag_name('table').text
		self.assertNotIn('ken', john_followed_by_table)
		self.client.get('http://localhost:5000/users/followers/ken')
		ken_followers_table = self.client.find_element_by_tag_name('table').text
		self.assertNotIn('john', ken_followers_table)
	

'''
	def test_follow_notifications(self):
		self.login_john()

		#john访问了ken的主页，关注了ken
		self.client.get('http://localhost:5000/users/user/ken')
		self.client.find_element_by_id('follow').click()

		#ken登录后发现收到了一条消息
		self.login_ken()
		ken_noti_num = self.client.find_element_by_class_name('badge-notification').text
		self.assertEqual(ken_noti_num, '1')

		#ken阅读了消息
		self.client.find_element_by_id('notifications').click()
		noti_card = self.client.find_element_by_class_name('card').text.replace('\n','').replace(' ','')
		self.assertIn('用户john关注了你', noti_card)


		#复原
		self.login_john()
		self.client.get('http://localhost:5000/users/user/ken')
		self.client.find_element_by_id('unfollow').click()
'''

