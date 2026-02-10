from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from django.core.management import call_command
from unittest.mock import patch
from deals.models import Deal, DealAudit
from accounts.models import PartnerOrganisation


User = get_user_model()


class DealTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Partners
        self.partner_org = PartnerOrganisation.objects.create(name='PartnerCo')
        self.partner_org2 = PartnerOrganisation.objects.create(name='PartnerTwo')
        self.partner_user = User.objects.create_user(username='p1', password='pass', role='PARTNER', partner_organisation=self.partner_org, email='p1@example.com')
        self.other_user = User.objects.create_user(username='p2', password='pass', role='PARTNER', partner_organisation=self.partner_org2, email='p2@example.com')
        # Brady and admin
        self.brady_user = User.objects.create_user(username='b1', password='pass', role='BRADY', email='b1@example.com')
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', role='ADMIN', email='admin@example.com')

        # Deals
        self.deal1 = Deal.objects.create(partner=self.partner_org, end_customer_name='ACME', project_name='D1', estimated_value=1000, product_category='PRINTERS', deal_type='NEW')
        self.deal2 = Deal.objects.create(partner=self.partner_org2, end_customer_name='OTHER', project_name='D2', estimated_value=2000, product_category='LABELS', deal_type='EXPANSION')
        # expired and near-expiry deals
        self.expired = Deal.objects.create(partner=self.partner_org, end_customer_name='Old', project_name='Expired', estimated_value=10, product_category='SOFTWARE', deal_type='REPLACEMENT', status='APPROVED', expiry_date=timezone.now().date() - timezone.timedelta(days=1))
        self.near_expiry = Deal.objects.create(partner=self.partner_org, end_customer_name='Soon', project_name='SoonExp', estimated_value=50, product_category='RFID', deal_type='NEW', status='APPROVED', expiry_date=timezone.now().date() + timezone.timedelta(days=3))

    def test_partner_cannot_view_other_partner_deal(self):
        self.client.login(username='p2', password='pass')
        res = self.client.get(f'/api/deals/{self.deal1.id}/')
        self.assertEqual(res.status_code, 404)

    def test_brady_can_view_any(self):
        self.client.login(username='b1', password='pass')
        res = self.client.get(f'/api/deals/{self.deal1.id}/')
        self.assertEqual(res.status_code, 200)

    def test_partner_create_sets_partner_and_defaults(self):
        self.client.login(username='p1', password='pass')
        payload = {
            'end_customer_name': 'NewCust',
            'project_name': 'NewProject',
            'estimated_value': '1234.56',
            'product_category': 'PRINTERS',
            'deal_type': 'NEW'
        }
        res = self.client.post('/api/deals/', payload, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['partner'], self.partner_org.id)
        self.assertEqual(res.data['status'], 'DRAFT')

    def test_partner_cannot_edit_non_draft_or_submitted(self):
        # mark deal as approved
        self.deal1.status = 'APPROVED'
        self.deal1.save()
        self.client.login(username='p1', password='pass')
        res = self.client.patch(f'/api/deals/{self.deal1.id}/', {'project_name': 'X'}, format='json')
        self.assertIn(res.status_code, (403, 400))

    def test_partner_submit_flow(self):
        self.client.login(username='p1', password='pass')
        res = self.client.post(f'/api/deals/{self.deal1.id}/submit/')
        self.assertEqual(res.status_code, 200)
        self.deal1.refresh_from_db()
        self.assertEqual(self.deal1.status, 'SUBMITTED')

    def test_brady_approve_sets_expiry_and_audit(self):
        # ensure deal is submittable
        self.deal1.status = 'SUBMITTED'
        self.deal1.save()
        self.client.login(username='b1', password='pass')
        res = self.client.post(f'/api/deals/{self.deal1.id}/approve/')
        self.assertEqual(res.status_code, 200)
        self.deal1.refresh_from_db()
        self.assertEqual(self.deal1.status, 'APPROVED')
        self.assertIsNotNone(self.deal1.expiry_date)
        # audit entry created
        audit = DealAudit.objects.filter(deal=self.deal1, new_status='APPROVED').exists()
        self.assertTrue(audit)

    def test_csv_export_partner_and_brady(self):
        # partner export: should only include partner_org deals
        self.client.login(username='p1', password='pass')
        res = self.client.get('/api/deals/export_csv/')
        self.assertEqual(res.status_code, 200)
        content = res.content.decode()
        self.assertIn('D1', content)
        self.assertNotIn('D2', content)

        # brady export: includes both
        self.client.login(username='b1', password='pass')
        res = self.client.get('/api/deals/export_csv/')
        self.assertEqual(res.status_code, 200)
        content = res.content.decode()
        self.assertIn('D1', content)
        self.assertIn('D2', content)

    def test_partner_dashboard_and_brady_dashboard(self):
        self.client.login(username='p1', password='pass')
        res = self.client.get('/api/deals/partner_dashboard/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(any(d['project_name'] == 'D1' for d in data))

        self.client.login(username='b1', password='pass')
        res = self.client.get('/api/deals/brady_dashboard/')
        self.assertEqual(res.status_code, 200)
        # paginated response
        self.assertIn('results', res.json())

    @patch('deals.management.commands.check_deal_expiry.send_mail')
    def test_expiry_command_marks_and_warns(self, mock_send_mail):
        # run management command
        call_command('check_deal_expiry')
        # expired deal should now have status EXPIRED
        self.expired.refresh_from_db()
        self.assertEqual(self.expired.status, 'EXPIRED')
        # near expiry should trigger an email (mocked)
        self.assertTrue(mock_send_mail.called)
