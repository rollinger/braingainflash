from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for Memo."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


#
# SIGNALS
#

# USER CREATION (post save)
@receiver(post_save, sender=User)
def user_created(sender, instance, **kwargs):
    if kwargs["created"]:
        # Add MemoSet Instance
        from cardset.models import MemoSet

        INITIAL_MEMOSET_NAME = _("General")
        initial_memoset = MemoSet(owner=instance, topic=INITIAL_MEMOSET_NAME)
        MemoSet.add_root(instance=initial_memoset)
