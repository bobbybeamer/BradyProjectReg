from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Notification


class NotificationsListView(LoginRequiredMixin, ListView):
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 50

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related('changed_by').order_by('-created_at')


class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        n = get_object_or_404(Notification.objects.only('id', 'read', 'recipient_id'), pk=pk, recipient=request.user)
        if not n.read:
            n.read = True
            n.save(update_fields=['read'])
        messages.success(request, 'Notification marked as read.')
        return redirect('notifications:list')


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')
