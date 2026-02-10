from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PartnerOrganisation


@admin.register(PartnerOrganisation)
class PartnerOrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Organization', {'fields': ('role', 'partner_organisation')}),
    )
    list_display = ('username', 'email', 'role', 'partner_organisation', 'is_staff')
    list_filter = ('role', 'is_staff')
