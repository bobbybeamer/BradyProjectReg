from django.core.management.base import BaseCommand
from deals.models import Deal


class Command(BaseCommand):
    help = 'Anonymize end-customer data for GDPR (example implementation)'

    def handle(self, *args, **options):
        # In a real implementation, you'd use retention policies, audit and strict logging
        affected = Deal.objects.exclude(end_customer_name__startswith='ANON').update(end_customer_name='ANONYMIZED')
        self.stdout.write(self.style.SUCCESS(f'Anonymized {affected} deals'))
