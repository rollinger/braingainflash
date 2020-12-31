#
# RULES Permissions
# https://github.com/dfunckt/django-rules
import rules


@rules.predicate
def is_creator(user, obj):
    if not obj:
        return False
    # print("%s => %s == %s => %s" % (obj, obj.creator, user, (obj.creator == user)))
    return obj.creator == user


# MemoCard Permissions
rules.add_rule("can_delete_memocard", is_creator)
rules.add_perm("cardset.delete_memocard", is_creator)


rules.add_rule("can_update_memocard", is_creator)
rules.add_rule("can_update_memocardperformance", is_creator)
