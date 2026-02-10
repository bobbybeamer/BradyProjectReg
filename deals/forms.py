from django import forms
from django.contrib.auth import get_user_model
from .models import Deal

User = get_user_model()

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            'project_name',
            'end_customer_name',
            'estimated_value',
            'product_category',
            'region',
            'deal_type',
            'internal_owner',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only Brady users should be selectable as internal_owner
        self.fields['internal_owner'].queryset = User.objects.filter(role__in=('BRADY', 'ADMIN'))
        self.fields['internal_owner'].required = False
