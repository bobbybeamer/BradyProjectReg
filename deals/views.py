from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import csv
from django.conf import settings
from datetime import timedelta
from .models import Deal
from .serializers import DealSerializer
from .permissions import DealPermissions
from .filters import DealFilter


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.select_related('partner', 'internal_owner').all()
    serializer_class = DealSerializer
    permission_classes = [DealPermissions]
    filterset_class = DealFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'PARTNER':
            return qs.filter(partner=user.partner_organisation)
        return qs

    def perform_update(self, serializer):
        # pass the user for audit logging
        instance = serializer.save()
        # note: signals will use instance._changed_by set in serializer.update

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        deal = self.get_object()
        if request.user.role == 'PARTNER' and deal.partner != request.user.partner_organisation:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if deal.status not in ('DRAFT',):
            return Response({'detail': 'Can only submit from Draft state'}, status=status.HTTP_400_BAD_REQUEST)
        deal.status = 'SUBMITTED'
        deal._changed_by = request.user
        deal.save()
        serializer = self.get_serializer(deal)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Brady users only
        if request.user.role not in ('BRADY', 'ADMIN'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        deal = self.get_object()
        deal.status = 'APPROVED'
        # determine expiry within configured bounds; default to min
        days = getattr(settings, 'DEAL_MIN_EXPIRY_DAYS', 90)
        deal.expiry_date = (deal.updated_at or deal.created_at).date() + timedelta(days=days)
        deal._changed_by = request.user
        deal.save()
        return Response(self.get_serializer(deal).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if request.user.role not in ('BRADY', 'ADMIN'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        deal = self.get_object()
        deal.status = 'REJECTED'
        deal._changed_by = request.user
        deal.save()
        return Response(self.get_serializer(deal).data)

    @action(detail=False, methods=['get'])
    def partner_dashboard(self, request):
        # lists own deals with status, value, expiry
        if request.user.role != 'PARTNER':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = self.filter_queryset(self.get_queryset())
        data = qs.values('id', 'project_name', 'status', 'estimated_value', 'expiry_date')
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def brady_dashboard(self, request):
        if request.user.role not in ('BRADY', 'ADMIN'):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = self.filter_queryset(self.get_queryset())
        # allow filters & sorting via query params
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        # check permissions: partners get only their deals by get_queryset
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="deals_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'partner', 'project_name', 'end_customer_name', 'status', 'estimated_value', 'expiry_date'])
        for d in qs:
            writer.writerow([d.id, d.partner.name, d.project_name, d.end_customer_name, d.status, str(d.estimated_value), d.expiry_date])
        return response
