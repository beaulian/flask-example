import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
	def test_password_setter(self):
		u = User(password="gavin")
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password="gavin")
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = User(password="gavin")
		self.assertTrue(u.verify_password("gavin"))
		self.assertFalse(u.verify_password("david"))

	def test_password_salts_are_random(self):
		u = User(password="gavin")
		u2 = User(password="gavin")
		self.assertTrue(u.password_hash 1= u2.password_hash)