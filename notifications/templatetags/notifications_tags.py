from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('notifications/bell.html', takes_context=True)
def notifications_bell(context, limit=5):
    user = context['user']
    if user.is_authenticated:
        qs = user.notifications.order_by('-created_at')[:limit]
        unread = user.notifications.filter(read=False).count()
    else:
        qs = []
        unread = 0
    return {'notifications': qs, 'unread_count': unread}
