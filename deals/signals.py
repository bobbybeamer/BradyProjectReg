from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Deal, DealAudit


@receiver(pre_save, sender=Deal)
def log_status_change(sender, instance: Deal, **kwargs):
    if not instance.pk:
        # new deal
        return
    try:
        old = Deal.objects.get(pk=instance.pk)
    except Deal.DoesNotExist:
        return
    if old.status != instance.status:
        # create audit entry
        DealAudit.objects.create(deal=instance, changed_by=getattr(instance, '_changed_by', None), old_status=old.status, new_status=instance.status)


@receiver(post_save, sender=Deal)
def notify_on_status_change(sender, instance: Deal, created, **kwargs):
    # simple in-app/email notification; in prod, use async tasks
    if created:
        return
    # check latest audit if status changed recently
    latest = instance.audit_trail.order_by('-timestamp').first()
    if latest:
        User = get_user_model()
        recipients_users = set()
        # partner users
        if instance.partner:
            for u in instance.partner.users.all():
                recipients_users.add(u)
        # for submitted deals, notify Brady users as well
        if latest.new_status == 'SUBMITTED':
            for u in User.objects.filter(role='BRADY'):
                recipients_users.add(u)
        # always include internal owner if present
        if instance.internal_owner:
            recipients_users.add(instance.internal_owner)

        # create in-app notifications
        try:
            from notifications.models import Notification
            for u in recipients_users:
                Notification.objects.create(
                    recipient=u,
                    changed_by=latest.changed_by,
                    verb=f"Deal {instance} status changed to {latest.new_status}",
                    description=f"Status changed from {latest.old_status} to {latest.new_status}."
                )
        except Exception:
            # notifications app may not be present or may fail; don't break flow
            pass

        # send emails to those that have addresses
        recipients = [u.email for u in recipients_users if u.email]
        subject = f"Deal {instance} status changed to {latest.new_status}"
        if recipients:
            send_mail(subject, f"Status changed from {latest.old_status} to {latest.new_status}.", settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
