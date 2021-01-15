import rules
from django import template

register = template.Library()


@register.simple_tag()
def get_group_membership(user, group):
    return group.membership_for(user)


@register.simple_tag()
def get_group_permissions(user, group):
    # returns permission dict for the group
    membership = group.membership_for(user)
    permissions = {
        "can_join_studygroup": rules.test_rule("can_join_studygroup", user, membership),
        "can_leave_studygroup": rules.test_rule(
            "can_leave_studygroup", user, membership
        ),
        "has_unapproved_membership": rules.test_rule(
            "has_unapproved_membership", user, membership
        ),
        "can_create_studygroup": rules.test_rule(
            "can_create_studygroup", user, membership
        ),
        "can_view_studygroup": rules.test_rule("can_view_studygroup", user, membership),
        "can_update_studygroup": rules.test_rule(
            "can_update_studygroup", user, membership
        ),
        "can_delete_studygroup": rules.test_rule(
            "can_delete_studygroup", user, membership
        ),
        "can_manage_member": rules.test_rule("can_manage_member", user, membership),
        "can_manage_card": rules.test_rule("can_manage_card", user, membership),
        "can_manage_topic": rules.test_rule("can_manage_topic", user, membership),
    }
    return permissions


@register.inclusion_tag("studygroups/templatetags/_group_icon.html")
def group_icon(group, max_height=35):
    # Add a group icon
    return {"group": group, "max_height": max_height}
