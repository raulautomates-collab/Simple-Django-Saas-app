
from django.test import TestCase
from django.conf import settings

# Create your tests here.
#testing the database url teet cse

class NeonDatabaseTestCase(TestCase):
    def test_db_url(self):
      DATABASE_URL=settings.DATABASE_URL
      self.assertIn('neon.tech',DATABASE_URL)