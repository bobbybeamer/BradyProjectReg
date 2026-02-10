from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


class Deal(models.Model):
    PRODUCT_CATEGORIES = [
        ('PRINTERS', 'Printers'),
        ('LABELS', 'Labels'),
        ('RFID', 'RFID'),
        ('SCANNERS', 'Scanners'),
        ('SOFTWARE', 'Software'),
    ]

    DEAL_TYPES = [('NEW', 'New'), ('EXPANSION', 'Expansion'), ('REPLACEMENT', 'Replacement')]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('CLOSED_WON', 'Closed Won'),
        ('CLOSED_LOST', 'Closed Lost'),
    ]

    partner = models.ForeignKey('accounts.PartnerOrganisation', on_delete=models.CASCADE, related_name='deals', db_index=True)
    end_customer_name = models.CharField(max_length=255, db_index=True)
    project_name = models.CharField(max_length=255, blank=True, db_index=True)
    description = models.TextField(blank=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], db_index=True)
    expected_close_date = models.DateField(null=True, blank=True)
    product_category = models.CharField(max_length=50, choices=PRODUCT_CATEGORIES, db_index=True)
    region = models.CharField(max_length=100, blank=True)
    deal_type = models.CharField(max_length=20, choices=DEAL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    internal_owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='owned_deals', db_index=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['partner', 'status']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.project_name or self.end_customer_name} - {self.partner.name}"


class DealAudit(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='audit_trail', db_index=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['deal', '-timestamp']),
        ]

    def __str__(self):
        return f"Deal {self.deal_id} changed to {self.new_status} at {self.timestamp}"
