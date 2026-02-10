from django.urls import path
from . import views_web as web

app_name = 'notifications'

urlpatterns = [
    path('', web.NotificationsListView.as_view(), name='list'),
    path('<int:pk>/mark-read/', web.MarkAsReadView.as_view(), name='mark_read'),
    path('mark-all-read/', web.MarkAllReadView.as_view(), name='mark_all_read'),
]
