from django.urls import path
from . import views_web as web

app_name = 'deals'

urlpatterns = [
    path('', web.my_deals_redirect, name='my_deals'),
    path('dashboard/', web.dashboard_redirect, name='dashboard'),
    path('partner/', web.PartnerDashboardView.as_view(), name='partner_deals'),
    path('partner/overview/', web.PartnerDashboardOverviewView.as_view(), name='partner_overview'),
    path('brady/', web.BradyDashboardView.as_view(), name='brady_deals'),
    path('brady/overview/', web.BradyDashboardOverviewView.as_view(), name='brady_overview'),
    path('create/', web.DealCreateView.as_view(), name='create_deal'),
    path('<int:pk>/', web.DealDetailView.as_view(), name='deal_detail'),
    path('<int:pk>/submit/', web.SubmitDealView.as_view(), name='submit_deal'),
    path('<int:pk>/approve/', web.ApproveDealView.as_view(), name='approve_deal'),
    path('<int:pk>/reject/', web.RejectDealView.as_view(), name='reject_deal'),
    path('<int:pk>/close-won/', web.CloseDealWonView.as_view(), name='close_deal_won'),
    path('<int:pk>/close-lost/', web.CloseDealLostView.as_view(), name='close_deal_lost'),
]
