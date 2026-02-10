from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, PartnerOrganisation

class NavbarTests(TestCase):
    def setUp(self):
        self.partner_org = PartnerOrganisation.objects.create(name='NavP')
        self.partner = User.objects.create_user('p2', password='pass', role='PARTNER', partner_organisation=self.partner_org)
        self.brady = User.objects.create_user('b2', password='pass', role='BRADY')
        self.admin = User.objects.create_user('a2', password='pass', role='ADMIN', is_superuser=True, is_staff=True)

    def test_partner_no_admin_in_nav(self):
        c = Client()
        c.login(username='p2', password='pass')
        r = c.get('/deals/partner/')
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, '/admin/')

    def test_brady_no_admin_in_nav(self):
        c = Client()
        c.login(username='b2', password='pass')
        r = c.get('/deals/brady/')
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, '/admin/')

    def test_admin_sees_admin_link_in_nav(self):
        c = Client()
        c.login(username='a2', password='pass')
        r = c.get('/deals/brady/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '/admin/')
