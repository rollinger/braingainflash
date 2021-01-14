from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# from studygroups.models import StudyGroup


class User(AbstractUser):
    """Default user for BrainGain."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def studygroups(self):
        # returns all studygroups where the user is an approved member of.
        # return Membership.objects.filter(member=self,approved=True)
        return  # StudyGroup.objects.filter(memberships__member=self)

    def has_free_group_slot(self):
        # How many groups are allowed in their plan and how much they have
        # STUB TODO
        return True

    def has_free_card_slot(self):
        # How many cards are allowed in their plan and how much they have
        # STUB TODO
        return True
