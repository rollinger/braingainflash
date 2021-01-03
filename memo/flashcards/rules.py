#
# RULES Permissions
# https://github.com/dfunckt/django-rules
import rules
from studygroups.models import Membership


@rules.predicate
def is_topic_createable(user, group):
    # returns if user is viewer in group
    # PARAMS: user & group
    if (
        group
        and Membership.objects.filter(group=group, member=user)
        .filter(role__in=["editor", "admin"])
        .exists()
    ):
        return True
    return False


@rules.predicate
def is_card_createable(user, group):
    # returns if user is editor in group
    # PARAMS: user & group
    if (
        group
        and Membership.objects.filter(group=group, member=user)
        .filter(role__in=["editor", "admin"])
        .exists()
    ):
        return True
    return False


@rules.predicate
def is_card_updateable(user, card):
    # can update card if user is admin or editor in group
    if (
        card
        and Membership.objects.filter(group=card.group, member=user)
        .filter(role__in=["editor", "admin"])
        .exists()
    ):
        return True
    return False


@rules.predicate
def is_card_deleteable(user, card):
    # can delete card if user is admin in group or card.creator
    if (
        card
        and Membership.objects.filter(group=card.group, member=user)
        .filter(role="admin")
        .exists()
        or card
        and card.creator == user
    ):
        return True
    return False


@rules.predicate
def is_performance_updateable(user, performance):
    # can update performance if user is the owner
    if performance and performance.owner == user:
        return True
    return False


# Card Permissions

rules.add_rule("can_create_topic", is_topic_createable)

rules.add_rule("can_create_card", is_card_createable)

rules.add_rule("can_update_card", is_card_updateable)
rules.add_rule("can_delete_card", is_card_deleteable)

rules.add_rule("can_update_performance", is_performance_updateable)
