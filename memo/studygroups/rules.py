#
# RULES Permissions for StudyGroup
# https://github.com/dfunckt/django-rules
import rules

# from studygroups.models import Membership

#
# Predicates
#


@rules.predicate()
def get_membership_object(user, group):
    membership = get_membership_object.context.get("membership")
    if membership is None:
        # retrieve and store in context if not present.
        membership = group.memberships.filter(member=user).first()
        get_membership_object.context["membership"] = membership
        return True
    else:
        return True
    return False


def NEW_check_group_member(user, group, approved=None, role=None):
    get_membership_object(user, group)
    membership = check_group_member.context.get("membership", default=None)
    check = False
    if membership:
        check = check | True
    if approved:
        check = check | (membership.approved == approved)
    if role:
        check = check | (membership.role == role)
    return check


def check_group_member(user, group, approved=None, role=None):
    # membership = Membership.objects.filter(group=group, member=user)
    membership = group.memberships.filter(member=user)
    if approved:
        membership = membership.filter(approved=approved)
    if role:
        membership = membership.filter(role=role)
    return membership.exists()


@rules.predicate
def has_membership_object(user, group):
    # user has a approved membership in the group
    return check_group_member(user, group)


@rules.predicate
def has_free_group_slot(user):
    # if user has a group_slot free
    return user.has_free_group_slot()


@rules.predicate
def has_free_card_slot(user):
    # if user has a card_slot free
    return user.has_free_card_slot()


@rules.predicate
def is_public_group(user, group):
    # weather the group is public or not
    # NOTE: user is needed here because rules uses positional *args
    return group.is_publicly_available


@rules.predicate
def is_main_user_group(user, group):
    # weather the group is main user space or not
    # NOTE: user is needed here because rules uses positional *args
    return group.is_main_user_group


@rules.predicate
def is_active_group_member(user, group):
    # user has a approved membership in the group
    return check_group_member(user, group, approved=True)


@rules.predicate
def is_inactive_group_member(user, group):
    # user has a approved membership in the group
    return not is_active_group_member(user, group)


@rules.predicate
def is_group_member_viewer(user, group):
    # user has a approved membership in the group
    return check_group_member(user, group, approved=True, role="viewer")


@rules.predicate
def is_group_member_editor(user, group):
    # user has a approved membership in the group
    return check_group_member(user, group, approved=True, role="editor")


@rules.predicate
def is_group_member_admin(user, group):
    # user has a approved membership in the group
    return check_group_member(user, group, approved=True, role="admin")


#
# Study Group RULES & PERMISSIONS
#
# Join and Leave Groups
is_group_joinable = (
    rules.is_authenticated
    & is_public_group
    & ~has_membership_object
    & has_free_group_slot
)
is_group_leaveable = (
    rules.is_authenticated
    & is_public_group
    & has_membership_object
    & ~is_group_member_admin
)
rules.add_rule("can_join_group", is_group_joinable)
rules.add_rule("can_leave_group", is_group_leaveable)
rules.add_rule(
    "has_unapproved_membership", has_membership_object & ~is_active_group_member
)

# can_create_group  => is_auth(user) & has_free_group_slot(user)
rules.add_rule("can_create_studygroup", rules.is_authenticated & has_free_group_slot)
rules.add_perm(
    "studygroups.add_studygroup", rules.is_authenticated & has_free_group_slot
)

# can_view_group    => is_auth(user) & is_approved_group_member(user, group)
rules.add_rule("can_view_group", rules.is_authenticated & is_active_group_member)
rules.add_perm(
    "studygroups.view_studygroup", rules.is_authenticated & is_active_group_member
)

# can_update_group  => is_auth(user) & is_group_admin(user, group)
rules.add_rule("can_update_group", rules.is_authenticated & is_group_member_admin)
rules.add_perm(
    "studygroups.edit_studygroup", rules.is_authenticated & is_group_member_admin
)

# can_delete_group  => is_auth(user) & is_group_admin(user, group)
rules.add_rule(
    "can_delete_group",
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
