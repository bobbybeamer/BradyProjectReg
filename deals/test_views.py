from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import Deal
from accounts.models import PartnerOrganisation

class WebViewsTest(TestCase):
    def setUp(self):
        self.partner_org = PartnerOrganisation.objects.create(name='TestPartner')
        self.partner = User.objects.create_user('puser', password='pass', role='PARTNER', partner_organisation=self.partner_org, email='puser@example.com')
        self.brady = User.objects.create_user('buser', password='pass', role='BRADY', email='buser@example.com')
        # create a draft deal for partner
        self.deal = Deal.objects.create(partner=self.partner_org, project_name='Web Test', end_customer_name='ACME', estimated_value=1000, product_category='PRINTERS', deal_type='NEW')

    def test_partner_sees_own_deals(self):
        c = Client()
        c.login(username='puser', password='pass')
        r = c.get(reverse('deals:partner_deals'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Web Test')

    def test_brady_sees_brady_dashboard(self):
        c = Client()
        c.login(username='buser', password='pass')
        r = c.get(reverse('deals:brady_deals'))
        self.assertEqual(r.status_code, 200)

    def test_partner_submit_flow(self):
        c = Client()
        c.login(username='puser', password='pass')
        resp = c.post(reverse('deals:submit_deal', args=[self.deal.id]))
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, 'SUBMITTED')

    def test_brady_approve_flow(self):
        # partner submits
        self.deal.status = 'SUBMITTED'
        self.deal.save()
        c = Client()
        c.login(username='buser', password='pass')
        resp = c.post(reverse('deals:approve_deal', args=[self.deal.id]))
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, 'APPROVED')
