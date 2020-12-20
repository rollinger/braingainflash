import uuid

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class BaseModelManager(models.Manager):
    pass


class BaseModel(models.Model):
    """
    Defines the abstract base model with uuid and timestamps
    """

    class Meta:
        abstract = True

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    objects = BaseModelManager()

    def __str__(self):
        return super(BaseModel, self).__str__()

    def save(self, *args, **kwargs):
        return super(BaseModel, self).save(*args, **kwargs)


class MemoSet(BaseModel):
    """
    A Set grouping a number of cards logically together. Supports subsets.
    """

    class Meta:
        verbose_name = _("Set")
        verbose_name_plural = _("Sets")
        unique_together = ("owner", "parent", "topic")

    # Parent as a Tree view (app)

    owner = models.ForeignKey(
        User,
        help_text=_("Memo Set is owned by this user"),
        null=True,
        blank=True,
        related_name="memosets",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "MemoSet",
        help_text=_("Parent Memo Set"),
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(
        _("Topic"), help_text=_("Topic of Memo Card"), max_length=255
    )
    is_template = models.BooleanField(
        _("Template"),
        help_text=_("This set can be forked by other users"),
        default=False,
    )
    # TODO: pause-toogle

    def fork_this(self, new_user):
        # returns a Memoset object tree copy for the new user
        pass

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.topic)

    def save(self, *args, **kwargs):
        return super(MemoSet, self).save(*args, **kwargs)


class MemoCard(BaseModel):
    """
    A card consisting of a question answer pairs to be memorize
    """

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    memoset = models.ForeignKey(
        MemoSet,
        help_text=_("Memo Card is assigned to this set"),
        related_name="memocards",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(
        _("Topic"), help_text=_("Topic of Memo Card"), max_length=255
    )
    question_text = models.TextField(_("Question (Text)"), max_length=2000)
    answer_text = models.TextField(_("Answer (Text)"), max_length=2000)
    # TODO: audio-pair, image-pair
    # Data contains the memorization data and statistics in json format:
    # {'training': [(datetime, training_outcome_int, training_duration_sec),...], 'n':0,'d':0,'o':0 }
    # Datetime in json is a string and must be properly decoded...
    data = JSONField(
        _("Memorization Data"), encoder=DjangoJSONEncoder, null=True, blank=True
    )
    score = models.DecimalField(
        _("Memorization Score"),
        help_text=_("Memo Card is assigned to this set"),
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    # TODO: pause-toogle

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.topic)

    def save(self, *args, **kwargs):
        return super(MemoCard, self).save(*args, **kwargs)
