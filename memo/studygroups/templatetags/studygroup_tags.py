from django import template

register = template.Library()


@register.simple_tag()
def get_group_permissions(user, group):
    # returns permission dict for the group
    # membership = group.membership_for(user)
    permissions = {
        "can_manage_card": False,
    }
    return permissions


@register.inclusion_tag("studygroups/templatetags/_group_icon.html")
def group_icon(group, max_height=35):
    # Add a group icon
    return {"group": group, "max_height": max_height}
