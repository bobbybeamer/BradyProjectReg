from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    # Root shows a simple demo landing page
    path('', RedirectView.as_view(url='/home/', permanent=False)),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Auth views for login/logout
    path('accounts/', include('django.contrib.auth.urls')),
    # Simple server-rendered dashboards & forms
    path('deals/', include('deals.urls')),
    path('notifications/', include('notifications.urls')),
]
