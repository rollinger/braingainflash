import rules
from rules.contrib.views import PermissionRequiredMixin


class CustomRulesPermissionRequiredMixin(PermissionRequiredMixin):
    # Overrides the has_permission method to work with my perms
    # (calling them directly rather than self.request.user.has_perms(perms, obj) )
    # See: https://github.com/dfunckt/django-rules/blob/master/rules/contrib/views.py LINE 47
    def has_permission(self):
        obj = self.get_permission_object()
        return rules.has_perm(self.permission_required, self.request.user, obj)
