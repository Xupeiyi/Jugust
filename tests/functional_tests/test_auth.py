#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import time
import unittest
from selenium import webdriver
from .base import FunctionalTest


class AuthTest(FunctionalTest):

	def test_register_then_confirm(self):

		#进入登录页面, 存在注册入口
		self.client.get('http://localhost:5000/auth/login')
		self.assertIn('点击这里注册', self.client.page_source)

		#进入注册页,为susan注册
		self.client.find_element_by_link_text('点击这里注册').click()
		self.client.find_element_by_name('email').send_keys('susan@example.com')
		self.client.find_element_by_name('username').send_keys('susan')
		self.client.find_element_by_name('password').send_keys('dog')
		self.client.find_element_by_name('password2').send_keys('dog')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('一封确认邮件已经发送至你的电子邮箱', self.client.page_source))

		#用susan新注册的帐号登录
		self.client.get('http://localhost:5000/auth/login')
		self.client.find_element_by_name('email').send_keys('susan@example.com')
		self.client.find_element_by_name('password').send_keys('dog')
		self.client.find_element_by_name('submit').click()

		#time.sleep(5)

		#页面上出现还未确认的提示
		self.assertIn('你还没有确认你的账号。', self.client.page_source.replace('\n',''))
		#假设确实收到邮件，得到确认令牌
		#这一部分测试有待改进, it's cheating!
		from app.models import User 
		user = User.query.filter_by(email='susan@example.com').first()
		token = user.generate_confirmation_token()
		url = 'http://localhost:5000/auth/confirm/%s/' %token
		
		#susan点击url确认,显示已确认
		self.client.get(url)
		self.assertIn('账户已确认！', self.client.page_source.replace('\n',''))

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
		
		#导航栏变为登录状态下
		self.assertTrue(re.search('退出', self.client.page_source))
		self.assertTrue(re.search('档案', self.client.page_source))
		self.assertTrue(re.search('消息', self.client.page_source))	


