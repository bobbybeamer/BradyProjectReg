from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PartnerOrganisation

class HomePageTests(TestCase):
    def setUp(self):
        self.partner_org = PartnerOrganisation.objects.create(name='HP')
        self.partner = User.objects.create_user('puser', password='pass', role='PARTNER', partner_organisation=self.partner_org)
        self.brady = User.objects.create_user('buser', password='pass', role='BRADY')
        self.admin = User.objects.create_user('auser', password='pass', role='ADMIN', is_superuser=True, is_staff=True)

    def test_partner_does_not_see_admin_link(self):
        c = Client()
        c.login(username='puser', password='pass')
        r = c.get('/home/')
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, '/admin/')
        # dashboard link present
        self.assertContains(r, 'Dashboard')

    def test_brady_does_not_see_admin_link(self):
        c = Client()
        c.login(username='buser', password='pass')
        r = c.get('/home/')
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, '/admin/')

    def test_admin_sees_admin_link(self):
        c = Client()
        c.login(username='auser', password='pass')
        r = c.get('/home/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '/admin/')
