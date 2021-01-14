from django import template

register = template.Library()


@register.inclusion_tag("studygroups/templatetags/_group_icon.html")
def group_icon(group, max_height=35):
    # Add a group icon
    return {"group": group, "max_height": max_height}
