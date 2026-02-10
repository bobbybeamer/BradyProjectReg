from django.contrib import admin
from .models import Deal, DealAudit


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'partner', 'status', 'estimated_value', 'expiry_date')
    list_filter = ('status', 'product_category', 'region', 'deal_type')
    search_fields = ('project_name', 'end_customer_name', 'partner__name')


@admin.register(DealAudit)
class DealAuditAdmin(admin.ModelAdmin):
    list_display = ('deal', 'old_status', 'new_status', 'changed_by', 'timestamp')
    readonly_fields = ('deal', 'old_status', 'new_status', 'changed_by', 'timestamp', 'note')
