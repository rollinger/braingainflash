#
# RULES Permissions
# https://github.com/dfunckt/django-rules
import rules
from django.db.models import Q
from studygroups.models import Membership


@rules.predicate
def is_group_viewable(user, group):
    # can view group if user has approved membership
    if (
        group
        and Membership.objects.filter(group=group, member=user, approved=True).exists()
    ):
        return True
    return False


@rules.predicate
def is_group_deleteable(user, group):
    # can delete group if user has approved membership and is admin and group is not main_user_group
    if (
        group
        and not group.is_main_user_group
        and Membership.objects.filter(
            group=group, member=user, approved=True, role="admin"
        ).exists()
    ):
        return True
    return False


@rules.predicate
def is_group_updateable(user, group):
    # can update group if user has approved membership and is admin
    if Membership.objects.filter(
        group=group, member=user, approved=True, role="admin"
    ).exists():
        return True
    return False


@rules.predicate
def is_group_joinable(user, group):
    # can join group if user does not have a membership and group is_publicly_available
    if (
        group
        and group.is_publicly_available
        and not Membership.objects.filter(group=group, member=user).exists()
    ):
        return True
    return False


@rules.predicate
def is_group_leaveable(user, group):
    # can leave group if group is not main_user_group and
    # user does have a membership and user is not admin
    if (
        group
        and not group.is_main_user_group
        and Membership.objects.filter(group=group, member=user)
        .filter(~Q(role="admin"))
        .exists()
    ):
        return True
    return False


@rules.predicate
def is_member_manageable(user, group):
    # Same as delete_permission
    return is_group_deleteable(user, group)


# Study Group Permissions
rules.add_rule("can_join_group", is_group_joinable)
rules.add_rule("can_leave_group", is_group_leaveable)
rules.add_rule("can_manage_member", is_member_manageable)
rules.add_rule("can_view_group", is_group_viewable)
rules.add_rule("can_delete_group", is_group_deleteable)
rules.add_rule("can_update_group", is_group_updateable)
