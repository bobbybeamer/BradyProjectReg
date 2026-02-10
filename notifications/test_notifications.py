from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch
from deals.models import Deal
from notifications.models import Notification
from accounts.models import PartnerOrganisation


User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.partner_org = PartnerOrganisation.objects.create(name='NotifPartner')
        self.partner_user = User.objects.create_user(username='pu', password='pass', role='PARTNER', partner_organisation=self.partner_org, email='pu@example.com')
        self.brady_user = User.objects.create_user(username='bu', password='pass', role='BRADY', email='bu@example.com')
        self.deal = Deal.objects.create(partner=self.partner_org, end_customer_name='ACME', project_name='Notify', estimated_value=100, product_category='PRINTERS', deal_type='NEW')

    @patch('deals.signals.send_mail')
    def test_submit_notifies_brady_and_partner(self, mock_send_mail):
        self.client.login(username='pu', password='pass')
        res = self.client.post(f'/api/deals/{self.deal.id}/submit/')
        self.assertEqual(res.status_code, 200)
        # brady should get a notification
        self.assertTrue(Notification.objects.filter(verb__icontains='SUBMITTED').exists())
        # partner user should also get a notification
        self.assertTrue(Notification.objects.filter(recipient=self.partner_user, verb__icontains='SUBMITTED').exists())
        # email attempted
        self.assertTrue(mock_send_mail.called)

    @patch('deals.signals.send_mail')
    def test_approve_notifies_partner(self, mock_send_mail):
        self.deal.status = 'SUBMITTED'
        self.deal.save()
        self.client.login(username='bu', password='pass')
        res = self.client.post(f'/api/deals/{self.deal.id}/approve/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Notification.objects.filter(recipient=self.partner_user, verb__icontains='APPROVED').exists())
        self.assertTrue(mock_send_mail.called)
