from django.test import TestCase

# Create your tests here.
class DemoTest(TestCase):
	def test_addition(self):
		self.assertEqual(1 + 1, 4)
