from rest_framework import routers
from django.urls import path, include
from deals.views import DealViewSet
from notifications.views_api import NotificationViewSet

router = routers.DefaultRouter()
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
