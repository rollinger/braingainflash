#
# RULES Permissions
# https://github.com/dfunckt/django-rules
import rules
from studygroups.rules import is_group_member_admin, is_group_member_editor


@rules.predicate
def can_manage_performance(user, performance):
    # user is owner of performance object
    if performance:
        return performance.owner == user
    return False


# can_manage_card  => is_auth(user) & is_group_editor(user, group) | is_group_admin(user, group)
# create, update
can_manage_card_to_studygroups = (
    rules.is_authenticated & is_group_member_admin | is_group_member_editor
)
rules.add_rule("can_manage_card", can_manage_card_to_studygroups)
rules.add_perm("studygroups.manage_studygroup_card", can_manage_card_to_studygroups)

# can_delete_card  => is_auth(user) & is_group_admin(user, group)
# delete
can_delete_card_in_studygroups = rules.is_authenticated & is_group_member_admin
rules.add_rule("can_delete_card", can_delete_card_in_studygroups)
rules.add_perm("studygroups.delete_studygroup_card", can_delete_card_in_studygroups)

# can_manage_topic => is_auth(user) & is_group_editor(user, group) | is_group_admin(user, group)
# create, update, delete
can_manage_topics_to_studygroups = (
    rules.is_authenticated & is_group_member_admin | is_group_member_editor
)
rules.add_rule("can_manage_topic", can_manage_topics_to_studygroups)
rules.add_perm("studygroups.manage_studygroup_topic", can_manage_topics_to_studygroups)

# can_manage_performance
rules.add_rule("can_manage_performance", can_manage_performance)
rules.add_perm("studygroups.manage_performance", can_manage_performance)
