#coding=utf-8
import sys,re
sys.path.append("../")

from selenium import webdriver
import unittest
import threading
import time
from app import create_app, db
from app.models import User, Role, Post

class SeleniumTestCase(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(cls):
		try:
			cls.client = webdriver.Firefox()
		except:
			pass

		if cls.client:
			# 创建程序
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			# 禁止日志,保持输出简洁
			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLevel("ERROR")

			# 创建数据库,并使用一些虚拟数据填充
			db.create_all()
			Role.insert_roles()
			User.generate_fake(10)
			Post.generate_fake(10)

			# 添加管理员
			admin_role = Role.query.filter_by(permissions=0xff).first()
			admin = User(email='john@example.com',
							username='john', password='cat',
							role=admin_role, confirmed=True)
			db.session.add(admin)
			db.session.commit()

			# 在一个线程中启动 Flask 服务器
			threading.Thread(target=cls.app.run).start()
			time.sleep(1)

	@classmethod
	def tearDownClass(cls):
		if cls.client:
			# 关闭 Flask 服务器和浏览器
			cls.client.get('http://127.0.0.1:5000/shutdown')
			cls.client.close()

			# 销毁数据库
			db.drop_all()
			db.session.remove()

			# 删除程序上下文
			cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not available')

	def tearDown(self):
		pass

	def test_admin_home_page(self):
	        # navigate to home page
	        self.client.get('http://127.0.0.1:5000/')
	        self.assertTrue(re.search('Hello,\s+Stranger!',
	                                  self.client.page_source))

	        # navigate to login page
	        self.client.find_element_by_link_text('登录').click()
	        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

	        # login
	        self.client.find_element_by_name('email').\
	            send_keys('john@example.com')
	        self.client.find_element_by_name('password').send_keys('cat')
	        self.client.find_element_by_name('submit').click()
	        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

	        # navigate to the user's profile page
	        self.client.find_element_by_link_text('john').click()
	        self.client.find_element_by_link_text('我的信息').click()
	        self.assertTrue('john' in self.client.page_source)


if __name__ == '__main__':
	unittest.main()

