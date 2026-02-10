from django.db import models
from django.contrib.auth.models import AbstractUser


class PartnerOrganisation(models.Model):
    STATUS_CHOICES = [("ACTIVE", "Active"), ("INACTIVE", "Inactive")]

    name = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner Organisation"
        verbose_name_plural = "Partner Organisations"
        indexes = [
            models.Index(fields=['status', 'name']),
        ]

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ("PARTNER", "Partner"),
        ("BRADY", "Brady"),
        ("ADMIN", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="PARTNER", db_index=True)
    partner_organisation = models.ForeignKey(
        PartnerOrganisation, null=True, blank=True, on_delete=models.SET_NULL, related_name='users', db_index=True
    )

    def save(self, *args, **kwargs):
        # Ensure users with ADMIN role are staff so they can access /admin/
        if self.role == 'ADMIN':
            self.is_staff = True
        super().save(*args, **kwargs)

    def is_partner(self):
        return self.role == "PARTNER"

    def is_brady(self):
        return self.role == "BRADY"

    def is_admin(self):
        return self.role == "ADMIN"
