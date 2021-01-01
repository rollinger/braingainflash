from cardset.models import MemoSet
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from studygroups.models import Membership, StudyGroup

User = get_user_model()


# USER CREATION (post save)
@receiver(post_save, sender=User)
def user_created(sender, instance, **kwargs):
    if kwargs["created"]:
        # Add a general user studygroup mit the user as admin
        main_study_group, created = StudyGroup.objects.get_or_create(
            name=_("{username}'s Study Space").format(
                username=instance.username.capitalize()
            ),
            description=_("Main study space for {username}").format(
                username=instance.username
            ),
            is_main_user_group=True,
            is_publicly_available=False,
            auto_approve_new_member=False,
        )
        membership, created = Membership.objects.get_or_create(
            member=instance, group=main_study_group, role="admin", approved=True
        )
        # Add general MemoSet Instance to studygroup
        INITIAL_MEMOSET_NAME = _("General")
        initial_memoset = MemoSet(
            studygroup=main_study_group, creator=instance, topic=INITIAL_MEMOSET_NAME
        )
        MemoSet.add_root(instance=initial_memoset)
