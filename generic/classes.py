from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminUserOrReadOnlyPermission(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or
                    super(IsAdminUserOrReadOnlyPermission, self).has_permission(request, view))
