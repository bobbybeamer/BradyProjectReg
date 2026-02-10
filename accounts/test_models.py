from django.test import TestCase
from accounts.models import User

class UserModelTests(TestCase):
    def test_admin_role_sets_is_staff(self):
        u = User.objects.create_user(username='admtest', password='pass', role='ADMIN', email='admtest@example.com')
        self.assertTrue(u.is_staff)

    def test_non_admin_role_does_not_force_is_staff(self):
        u = User.objects.create_user(username='ptest', password='pass', role='PARTNER', email='ptest@example.com')
        self.assertFalse(u.is_staff)
