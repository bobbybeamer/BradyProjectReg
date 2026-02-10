from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from deals.models import Deal
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Check deal expiry statuses and notify if nearing expiry or expired'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # expire deals past expiry_date
        expired = Deal.objects.filter(expiry_date__lt=today).exclude(status='EXPIRED')
        count = expired.update(status='EXPIRED')
        self.stdout.write(self.style.SUCCESS(f'Marked {count} deals as EXPIRED'))

        # warn deals approaching expiry in next 7 days
        warn_date = today + timedelta(days=7)
        expiring = Deal.objects.filter(expiry_date__range=(today, warn_date)).exclude(status__in=('EXPIRED', 'CLOSED_WON', 'CLOSED_LOST'))
        for deal in expiring:
            recipients = [u.email for u in deal.partner.users.all() if u.email]
            if deal.internal_owner and deal.internal_owner.email:
                recipients.append(deal.internal_owner.email)
            recipients = list(set(recipients))
            if recipients:
                send_mail(f'Deal {deal} nearing expiry', f'Deal {deal} will expire on {deal.expiry_date}', settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
        self.stdout.write(self.style.SUCCESS(f'Alerted {expiring.count()} deals nearing expiry'))
