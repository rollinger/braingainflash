from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from utils.abstract_models import TimestampMixin, UUIDMixin

User = get_user_model()

STUDYGROUP_ROLES = (
    (0, _("Viewer")),  # view_perm
    (1, _("Editor")),  # view_perm, update_perm
    (2, _("Admin")),  # view_perm, update_perm, create_perm, delete_perm
)

STUDYGROUP_JOIN_MODE = (
    (0, _("Public")),  # free public join
    (1, _("Managed")),  # managed join
    (2, _("Private")),  # join is closed
)


class StudyGroupManager(models.Manager):
    pass


class StudyGroup(UUIDMixin, TimestampMixin, models.Model):
    """
    A study group of users co-learing a subject matter
    """

    class Meta:
        verbose_name = _("Study Group")
        verbose_name_plural = _("Study Groups")

    name = models.CharField(
        _("Group Title"),
        help_text=_("Name of the group"),
        max_length=255,
    )
    slug = models.SlugField(
        _("Group Slug"),
        help_text=_("URL part of the study group"),
        max_length=50,
        allow_unicode=True,
        unique=True,
    )
    description = RichTextField(_("Description of Study Group"), max_length=2000)

    is_main_user_group = models.BooleanField(
        _("Main User Group"),
        help_text=_("If this is the main user group"),
        default=False,
    )

    join_mode = models.PositiveSmallIntegerField(
        _("Join Group Mode"),
        help_text=_("How new members can join"),
        choices=STUDYGROUP_JOIN_MODE,
        default=2,
    )

    new_member_role = models.PositiveSmallIntegerField(
        _("Default member role"),
        help_text=_("Default role of new member"),
        choices=STUDYGROUP_ROLES,
        default=0,
    )

    objects = StudyGroupManager()

    def __str__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        # Returns path to update-view
        pass  # return reverse("memocard_update_view", kwargs={"unique_id": self.unique_id})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class MembershipManager(models.Manager):
    pass


class Membership(UUIDMixin, TimestampMixin, models.Model):
    """
    A membership of a user in a studygroup with permissions
    """

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")

    member = models.ForeignKey(
        User,
        help_text=_("User of the relation"),
        related_name="memberships",
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        StudyGroup,
        help_text=_("Study Group of the relation"),
        related_name="memberships",
        on_delete=models.CASCADE,
    )

    role = models.PositiveSmallIntegerField(
        _("Role"),
        help_text=_("Member's role in study group"),
        choices=STUDYGROUP_ROLES,
        default=0,
    )

    objects = MembershipManager()

    def __str__(self):
        return "%s is %s in %s" % (self.member, self.get_role_display(), self.group)

    def get_absolute_url(self):
        # Returns path to update-view
        pass  # return reverse("memocard_update_view", kwargs={"unique_id": self.unique_id})
