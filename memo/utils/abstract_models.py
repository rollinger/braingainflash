import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


class UUIDMixin(models.Model):
    """
    Adds unique uuid to Model and streamlines get_absolute_url for reverse
    """

    class Meta:
        abstract = True

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_absolute_url(self):
        # Interface must be specified in the sub class
        return super(UUIDMixin, self).get_absolute_url()


class TimestampMixin(models.Model):
    """
    Defines the abstract timestamps for models
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def save(self, *args, **kwargs):
        return super(TimestampMixin, self).save(*args, **kwargs)
