import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from treebeard.ns_tree import NS_Node

User = get_user_model()


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


class MemoSet(UUIDMixin, NS_Node):
    """
    A Set grouping a number of cards logically together. Supports subsets with the
    treebeard Nested Sets Node. https://django-treebeard.readthedocs.io/en/latest/ns_tree.html
    """

    node_order_by = ["topic"]

    class Meta:
        verbose_name = _("Set")
        verbose_name_plural = _("Sets")

    owner = models.ForeignKey(
        User,
        help_text=_("Memo Set is owned by this user"),
        related_name="memosets",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(
        _("Topic"), help_text=_("Topic of Memo Card"), max_length=255
    )

    # TODO: pause-toogle
    # TODO: is-template => able to fork the set including tree and cards

    def __str__(self):
        return "%s: %s (%s)" % (self._meta.verbose_name, self.topic, self.owner)

    def get_absolute_url(self):
        # Returns path to detail-view
        return reverse("memoset.views.details", args=[str(self.unique_id)])

    def save(self, *args, **kwargs):
        return super(MemoSet, self).save(*args, **kwargs)


class MemoCardManager(models.Manager):
    pass


class MemoCard(UUIDMixin, TimestampMixin, models.Model):
    """
    A card consisting of a question answer pairs to be memorize
    """

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    memoset = models.ForeignKey(
        MemoSet,
        help_text=_("Memo Card is assigned to this set"),
        related_name="cards",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(
        _("Topic"), help_text=_("Topic of Memo Card"), max_length=255
    )
    # Card Content
    question_text = models.TextField(_("Question (Text)"), max_length=2000)
    answer_text = models.TextField(_("Answer (Text)"), max_length=2000)
    # TODO: audio-pair, image-pair

    # Data contains the memorization data for memorization statistics in json format.
    # See: https://github.com/rpkilby/jsonfield
    # Data Format:
    # { 'learning': [(datetime, outcome_int, duration_sec),...],
    #   'recalling': [(datetime, outcome_int, duration_sec),...]
    # }
    data = JSONField(_("Memorization Data"), null=True, blank=True)

    score = models.DecimalField(
        _("Memorization Score"),
        help_text=_("Memorization Score of the Memo Card"),
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    # TODO: pause-toogle

    objects = MemoCardManager()

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.topic)

    def get_absolute_url(self):
        # Returns path to detail-view
        return reverse("memocard.views.details", args=[str(self.unique_id)])

    def save(self, *args, **kwargs):
        return super(MemoCard, self).save(*args, **kwargs)
