from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, View, TemplateView
from django.contrib import messages
from .models import Deal
from .forms import DealForm
from accounts.models import PartnerOrganisation


class RoleRequiredMixin(UserPassesTestMixin):
    role = None

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == self.role or self.request.user.is_superuser)


class PartnerDashboardOverviewView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'deals/partner_overview.html'
    role = 'PARTNER'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partner = self.request.user.partner_organisation
        # Use aggregate for efficient counting and summing
        from django.db.models import Count, Sum, Q
        deals_qs = Deal.objects.filter(partner=partner)
        stats = deals_qs.aggregate(
            total_deals=Count('id'),
            draft_deals=Count('id', filter=Q(status='DRAFT')),
            submitted_deals=Count('id', filter=Q(status='SUBMITTED')),
            approved_deals=Count('id', filter=Q(status='APPROVED')),
            rejected_deals=Count('id', filter=Q(status='REJECTED')),
            total_value=Sum('estimated_value')
        )
        context.update(stats)
        context['total_value'] = stats['total_value'] or 0
        return context


class PartnerDashboardView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'deals/partner_dashboard.html'
    context_object_name = 'deals'
    model = Deal
    role = 'PARTNER'
    paginate_by = 20

    def get_queryset(self):
        qs = Deal.objects.filter(partner=self.request.user.partner_organisation).select_related('partner')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        
        # Sort
        sort_by = self.request.GET.get('sort', '-updated_at')
        qs = qs.order_by(sort_by)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['sort_by'] = self.request.GET.get('sort', '-updated_at')
        context['deal_statuses'] = Deal.STATUS_CHOICES
        context['sort_options'] = [
            ('-updated_at', 'Last Updated (Newest)'),
            ('updated_at', 'Last Updated (Oldest)'),
            ('-created_at', 'Created (Newest)'),
            ('created_at', 'Created (Oldest)'),
            ('-estimated_value', 'Value (High to Low)'),
            ('estimated_value', 'Value (Low to High)'),
            ('project_name', 'Project Name (A-Z)'),
            ('-project_name', 'Project Name (Z-A)'),
        ]
        return context


class BradyDashboardOverviewView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    template_name = 'deals/brady_overview.html'
    role = 'BRADY'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use aggregate for efficient counting and summing
        from django.db.models import Count, Sum, Q
        stats = Deal.objects.aggregate(
            total_deals=Count('id'),
            draft_deals=Count('id', filter=Q(status='DRAFT')),
            submitted_deals=Count('id', filter=Q(status='SUBMITTED')),
            approved_deals=Count('id', filter=Q(status='APPROVED')),
            rejected_deals=Count('id', filter=Q(status='REJECTED')),
            total_value=Sum('estimated_value')
        )
        context.update(stats)
        context['total_value'] = stats['total_value'] or 0
        return context


class BradyDashboardView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    template_name = 'deals/brady_dashboard.html'
    context_object_name = 'deals'
    model = Deal
    role = 'BRADY'
    paginate_by = 20

    def get_queryset(self):
        qs = Deal.objects.select_related('partner', 'internal_owner')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        
        # Filter by partner
        partner = self.request.GET.get('partner')
        if partner:
            qs = qs.filter(partner__id=partner)
        
        # Sort
        sort_by = self.request.GET.get('sort', '-updated_at')
        qs = qs.order_by(sort_by)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only fetch active partners with minimal fields
        context['partners'] = PartnerOrganisation.objects.filter(status='ACTIVE').only('id', 'name').order_by('name')
        context['status_filter'] = self.request.GET.get('status', '')
        context['partner_filter'] = self.request.GET.get('partner', '')
        context['sort_by'] = self.request.GET.get('sort', '-updated_at')
        context['deal_statuses'] = Deal.STATUS_CHOICES
        context['sort_options'] = [
            ('-updated_at', 'Last Updated (Newest)'),
            ('updated_at', 'Last Updated (Oldest)'),
            ('-created_at', 'Created (Newest)'),
            ('created_at', 'Created (Oldest)'),
            ('-estimated_value', 'Value (High to Low)'),
            ('estimated_value', 'Value (Low to High)'),
            ('project_name', 'Project Name (A-Z)'),
            ('-project_name', 'Project Name (Z-A)'),
        ]
        return context


class DealCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    template_name = 'deals/deal_form.html'
    form_class = DealForm
    role = 'PARTNER'

    def form_valid(self, form):
        deal = form.save(commit=False)
        # Assign to partner automatically
        deal.partner = self.request.user.partner_organisation
        deal._changed_by = self.request.user
        deal.save()
        messages.success(self.request, 'Deal created in Draft status.')
        return redirect('deals:my_deals')


class DealDetailView(LoginRequiredMixin, DetailView):
    template_name = 'deals/deal_detail.html'
    model = Deal
    context_object_name = 'deal'

    def get(self, request, *args, **kwargs):
        deal = self.get_object()
        # Permission checks: partners only view their deals
        if request.user.role == 'PARTNER' and deal.partner != request.user.partner_organisation:
            messages.error(request, 'Forbidden')
            return redirect('deals:my_deals')
        return super().get(request, *args, **kwargs)


class SubmitDealView(LoginRequiredMixin, View):
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        if request.user.role != 'PARTNER' or deal.partner != request.user.partner_organisation:
            messages.error(request, 'Forbidden')
            return redirect('deals:deal_detail', pk=pk)
        if deal.status != 'DRAFT':
            messages.warning(request, 'Only Draft deals can be submitted.')
            return redirect('deals:deal_detail', pk=pk)
        deal.status = 'SUBMITTED'
        deal._changed_by = request.user
        deal.save()
        messages.success(request, 'Deal submitted for review.')
        return redirect('deals:deal_detail', pk=pk)


class ApproveDealView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role not in ('BRADY', 'ADMIN'):
            messages.error(request, 'Forbidden')
            return redirect('deals:deal_detail', pk=pk)
        deal = get_object_or_404(Deal, pk=pk)
        deal.status = 'APPROVED'
        # set expiry
        from django.conf import settings
        from datetime import timedelta
        days = getattr(settings, 'DEAL_MIN_EXPIRY_DAYS', 90)
        deal.expiry_date = (deal.updated_at or deal.created_at).date() + timedelta(days=days)
        deal._changed_by = request.user
        deal.save()
        messages.success(request, 'Deal approved.')
        return redirect('deals:deal_detail', pk=pk)


class RejectDealView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role not in ('BRADY', 'ADMIN'):
            messages.error(request, 'Forbidden')
            return redirect('deals:deal_detail', pk=pk)
        deal = get_object_or_404(Deal, pk=pk)
        deal.status = 'REJECTED'
        deal._changed_by = request.user
        deal.save()
        messages.success(request, 'Deal rejected.')
        return redirect('deals:deal_detail', pk=pk)


class CloseDealWonView(LoginRequiredMixin, View):
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        # Partners can only close their own deals
        if request.user.role == 'PARTNER' and deal.partner != request.user.partner_organisation:
            messages.error(request, 'Forbidden')
            return redirect('deals:deal_detail', pk=pk)
        # Only approved deals can be closed won
        if deal.status != 'APPROVED':
            messages.warning(request, 'Only Approved deals can be closed won.')
            return redirect('deals:deal_detail', pk=pk)
        deal.status = 'CLOSED_WON'
        deal._changed_by = request.user
        deal.save()
        messages.success(request, 'Deal marked as Closed Won.')
        return redirect('deals:deal_detail', pk=pk)


class CloseDealLostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        # Partners can only close their own deals
        if request.user.role == 'PARTNER' and deal.partner != request.user.partner_organisation:
            messages.error(request, 'Forbidden')
            return redirect('deals:deal_detail', pk=pk)
        # Only approved deals can be closed lost
        if deal.status != 'APPROVED':
            messages.warning(request, 'Only Approved deals can be closed lost.')
            return redirect('deals:deal_detail', pk=pk)
        deal.status = 'CLOSED_LOST'
        deal._changed_by = request.user
        deal.save()
        messages.success(request, 'Deal marked as Closed Lost.')
        return redirect('deals:deal_detail', pk=pk)


def my_deals_redirect(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse_lazy('login'), request.path))
    if request.user.role == 'PARTNER':
        return redirect('deals:partner_deals')
    return redirect('deals:brady_deals')


def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (reverse_lazy('login'), request.path))
    if request.user.role == 'PARTNER':
        return redirect('deals:partner_overview')
    return redirect('deals:brady_overview')
