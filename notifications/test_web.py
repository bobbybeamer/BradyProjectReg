from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from notifications.models import Notification

class NotificationsWebTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('nuser', password='pass', role='BRADY')
        Notification.objects.create(recipient=self.user, verb='Test', description='Hello')
        Notification.objects.create(recipient=self.user, verb='Later', description='Another')

    def test_list_and_mark_read(self):
        c = Client()
        c.login(username='nuser', password='pass')
        r = c.get(reverse('notifications:list'))
        self.assertContains(r, 'Test')
        # mark first as read
        n = Notification.objects.filter(recipient=self.user).first()
        resp = c.post(reverse('notifications:mark_read', args=[n.id]))
        self.assertEqual(resp.status_code, 302)
        n.refresh_from_db()
        self.assertTrue(n.read)

    def test_mark_all_read(self):
        c = Client()
        c.login(username='nuser', password='pass')
        resp = c.post(reverse('notifications:mark_all_read'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Notification.objects.filter(recipient=self.user, read=False).count(), 0)
