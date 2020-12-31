#
# RULES Permissions
# https://github.com/dfunckt/django-rules
import rules
from studygroups.models import Membership


@rules.predicate
def is_group_joinable(user, group):
    # can join if user does not have a membership and group is_publicly_available
    if (
        group
        and group.is_publicly_available
        and not Membership.objects.filter(group=group, member=user).exists()
    ):
        return True
    return False


@rules.predicate
def is_group_viewable(user, group):
    # can view group if user has approved membership
    if Membership.objects.filter(group=group, member=user, approved=True).exists():
        return True
    return False


@rules.predicate
def is_group_deleteable(user, group):
    # can delete group if user has approved membership and is admin and group is not main_user_group
    if (
        not group.is_main_user_group
        and Membership.objects.filter(
            group=group, member=user, approved=True, role="admin"
        ).exists()
    ):
        return True
    return False


# Study Group Permissions
rules.add_rule("can_join_group", is_group_joinable)
rules.add_rule("can_view_group", is_group_viewable)
rules.add_rule("can_delete_group", is_group_deleteable)
