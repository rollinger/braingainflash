#
# RULES Permissions for StudyGroup
# https://github.com/dfunckt/django-rules
import rules

# from studygroups.models import Membership

#
# NEW PERMISSION SYSTEM
#


@rules.predicate
def has_free_group_slot(user):
    # if user has a group_slot free
    return user.has_free_group_slot()


@rules.predicate
def has_free_card_slot(user):
    # if user has a card_slot free
    return user.has_free_card_slot()


@rules.predicate
def has_membership_object(user, membership):
    # user has membership object for the group
    if membership:
        return True
    return False


@rules.predicate
def is_public_group(user, membership):
    # weather the group is public or not
    # NOTE: user is needed here because rules uses positional *args
    return membership.group.is_publicly_available


@rules.predicate
def is_main_user_group(user, membership):
    # weather the group is main user space or not
    # NOTE: user is needed here because rules uses positional *args
    return membership.group.is_main_user_group


@rules.predicate
def is_active_group_member(user, membership):
    # user has a approved membership in the group
    if membership:
        return membership.approved
    return False


@rules.predicate
def is_inactive_group_member(user, membership):
    # user has a approved membership in the group
    if membership:
        return not membership.approved
    return True


@rules.predicate
def is_group_member_viewer(user, membership):
    # user has a approved viewer membership in the group
    if membership:
        return (membership.approved is True) & (membership.role == "viewer")
    return False


@rules.predicate
def is_group_member_editor(user, membership):
    # user has a approved editor membership in the group
    if membership:
        return (membership.approved is True) & (membership.role == "editor")
    return False


@rules.predicate
def is_group_member_admin(user, membership):
    # user has a approved admin membership in the group
    if membership:
        return (membership.approved is True) & (membership.role == "admin")
    return False


#
# Study Group RULES & PERMISSIONS
#
# Join and Leave Groups
is_group_joinable = (
    rules.is_authenticated & ~has_membership_object & has_free_group_slot
)
is_group_leaveable = (
    rules.is_authenticated & has_membership_object & ~is_group_member_admin
)
rules.add_rule("can_join_studygroup", is_group_joinable)
rules.add_rule("can_leave_studygroup", is_group_leaveable)
rules.add_rule(
    "has_unapproved_membership", has_membership_object & ~is_active_group_member
)

# can_create_group  => is_auth(user) & has_free_group_slot(user)
rules.add_rule("can_create_studygroup", rules.is_authenticated & has_free_group_slot)
rules.add_perm(
    "studygroups.add_studygroup", rules.is_authenticated & has_free_group_slot
)

# can_view_group    => is_auth(user) & is_approved_group_member(user, group)
rules.add_rule("can_view_studygroup", rules.is_authenticated & is_active_group_member)
rules.add_perm(
    "studygroups.view_studygroup", rules.is_authenticated & is_active_group_member
)

# can_update_group  => is_auth(user) & is_group_admin(user, group)
rules.add_rule("can_update_studygroup", rules.is_authenticated & is_group_member_admin)
rules.add_perm(
    "studygroups.edit_studygroup", rules.is_authenticated & is_group_member_admin
)

# can_delete_group  => is_auth(user) & is_group_admin(user, group)
rules.add_rule(
    "can_delete_studygroup",
    rules.is_authenticated & is_group_member_admin & ~is_main_user_group,
)
rules.add_perm(
    "studygroups.delete_studygroup",
    rules.is_authenticated & is_group_member_admin & ~is_main_user_group,
)

# manage_studygroup_memberships => is_auth(user) & is_group_admin(user, group)
rules.add_rule("can_manage_member", rules.is_authenticated & is_group_member_admin)
rules.add_perm(
    "studygroups.manage_studygroup_memberships",
    rules.is_authenticated & is_group_member_admin,
)
