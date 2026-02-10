from rest_framework import permissions


class DealPermissions(permissions.BasePermission):
    """Role & object-level permission enforcement"""

    def has_permission(self, request, view):
        # authenticated users only
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        if user.role == 'BRADY':
            return True
        if user.role == 'PARTNER':
            # partners can only access deals in their organisation
            if obj.partner_id != getattr(user.partner_organisation, 'id', None):
                return False
            # partners can edit only when status is Draft or Submitted
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.status in ('DRAFT', 'SUBMITTED')
        return False
