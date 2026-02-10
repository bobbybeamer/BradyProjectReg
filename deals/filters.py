import django_filters
from .models import Deal


class DealFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    partner = django_filters.NumberFilter(field_name='partner__id')
    region = django_filters.CharFilter(field_name='region', lookup_expr='icontains')
    product_category = django_filters.CharFilter(field_name='product_category')

    class Meta:
        model = Deal
        fields = ['status', 'partner', 'region', 'product_category']
