from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import PartnerOrganisation
from deals.models import Deal
from django.utils import timezone
from django.conf import settings
import random


User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data: partner orgs, users, and sample deals'

    def handle(self, *args, **options):
        out = self.stdout
        
        # Create 6 partner organisations
        partner_names = [
            'TechSolutions Ltd',
            'GlobalPrint Inc',
            'DataStream Partners',
            'Enterprise Systems Co',
            'SecureLabel Technologies',
            'Innovation Labs Group'
        ]
        
        partners = []
        partner_users = []
        
        for idx, name in enumerate(partner_names, 1):
            partner, _ = PartnerOrganisation.objects.get_or_create(name=name)
            partners.append(partner)
            
            # Create partner user
            username = f'partner{idx}'
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': f'{username}@example.com',
                'role': 'PARTNER',
                'partner_organisation': partner
            })
            if created:
                user.set_password(f'{username}pass')
                user.save()
            partner_users.append(user)
            out.write(f'Created partner: {name} (user: {username}/{username}pass)')
        
        # Create Brady and Admin users
        brady1, created = User.objects.get_or_create(username='brady1', defaults={
            'email': 'brady1@example.com', 'role': 'BRADY'
        })
        if created:
            brady1.set_password('brady1pass')
            brady1.save()
        
        admin1, created = User.objects.get_or_create(username='admin1', defaults={
            'email': 'admin1@example.com',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            admin1.set_password('admin1pass')
            admin1.save()
        
        # Sample data lists
        project_prefixes = ['Project', 'Deal', 'Opportunity', 'Contract', 'Initiative']
        project_types = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Prime', 'Elite', 'Premium', 'Standard', 'Express']
        customers = [
            'Acme Corporation', 'Global Industries', 'TechCorp Ltd', 'MegaSystems Inc',
            'Enterprise Solutions', 'DataCentre UK', 'Manufacturing Co', 'Retail Chain Ltd',
            'Healthcare Systems', 'Finance Group', 'LogisticsPro', 'Education Trust',
            'Government Dept', 'Transport Authority', 'Energy Partners', 'Telecom Services',
            'Insurance Group', 'Banking Corp', 'Media Holdings', 'Hospitality Ltd'
        ]
        product_categories = ['PRINTERS', 'LABELS', 'SOFTWARE', 'SCANNERS', 'RIBBONS']
        deal_types = ['NEW', 'EXPANSION', 'RENEWAL']
        statuses = ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'EXPIRED', 'CLOSED_WON', 'CLOSED_LOST']
        
        # Create 124 deals with varied data
        deals_created = 0
        for i in range(1, 125):
            partner = random.choice(partners)
            partner_user = partner_users[partners.index(partner)]
            
            project_name = f"{random.choice(project_prefixes)} {random.choice(project_types)} {i:03d}"
            customer = random.choice(customers)
            value = random.randint(500, 100000)
            product = random.choice(product_categories)
            deal_type = random.choice(deal_types)
            
            # Create deal
            deal, created = Deal.objects.get_or_create(
                partner=partner,
                project_name=project_name,
                defaults={
                    'end_customer_name': customer,
                    'estimated_value': value,
                    'product_category': product,
                    'deal_type': deal_type,
                }
            )
            
            if created:
                # Randomly assign status with realistic distribution
                rand = random.random()
                if rand < 0.15:  # 15% draft
                    target_status = 'DRAFT'
                elif rand < 0.35:  # 20% submitted
                    target_status = 'SUBMITTED'
                elif rand < 0.45:  # 10% under review
                    target_status = 'UNDER_REVIEW'
                elif rand < 0.65:  # 20% approved
                    target_status = 'APPROVED'
                elif rand < 0.75:  # 10% rejected
                    target_status = 'REJECTED'
                elif rand < 0.80:  # 5% expired
                    target_status = 'EXPIRED'
                elif rand < 0.90:  # 10% closed won
                    target_status = 'CLOSED_WON'
                else:  # 10% closed lost
                    target_status = 'CLOSED_LOST'
                
                # Update status with proper workflow
                if target_status != 'DRAFT':
                    # First submit
                    deal.status = 'SUBMITTED'
                    deal._changed_by = partner_user
                    deal.save()
                    
                    if target_status in ['UNDER_REVIEW', 'APPROVED', 'REJECTED']:
                        if target_status == 'UNDER_REVIEW':
                            deal.status = 'UNDER_REVIEW'
                            deal._changed_by = brady1
                            deal.save()
                        elif target_status == 'APPROVED':
                            deal.status = 'APPROVED'
                            days = getattr(settings, 'DEAL_MIN_EXPIRY_DAYS', 90)
                            deal.expiry_date = (deal.updated_at or deal.created_at).date() + timezone.timedelta(days=days)
                            deal._changed_by = brady1
                            deal.save()
                        elif target_status == 'REJECTED':
                            deal.status = 'REJECTED'
                            deal._changed_by = brady1
                            deal.save()
                    elif target_status in ['EXPIRED', 'CLOSED_WON', 'CLOSED_LOST']:
                        # First approve
                        deal.status = 'APPROVED'
                        days = getattr(settings, 'DEAL_MIN_EXPIRY_DAYS', 90)
                        deal.expiry_date = (deal.updated_at or deal.created_at).date() + timezone.timedelta(days=days)
                        deal._changed_by = brady1
                        deal.save()
                        
                        # Then move to final status
                        deal.status = target_status
                        deal._changed_by = partner_user
                        deal.save()
                
                deals_created += 1
        
        out.write(self.style.SUCCESS(f'\n✓ Successfully seeded test data!'))
        out.write(f'  Partners: {len(partners)}')
        out.write(f'  Partner users: {len(partner_users)} (partner1/partner1pass through partner6/partner6pass)')
        out.write(f'  Brady users: brady1/brady1pass')
        out.write(f'  Admin users: admin1/admin1pass')
        out.write(f'  Deals created: {deals_created}')
