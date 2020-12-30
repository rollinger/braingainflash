import datetime
import random
import uuid

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from treebeard.ns_tree import NS_Node, NS_NodeManager

User = get_user_model()

# 1) Model definitions
# 2) Rules permissions
# 3) Signal handling


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


class MemoSetManager(NS_NodeManager):
    def get_by_unique_id(self, unique_id):
        return self.filter(unique_id=uuid.UUID(str(unique_id))).first()


class MemoSet(UUIDMixin, NS_Node):
    """
    A Set grouping a number of cards logically together. Supports subsets with the
    treebeard Nested Sets Node. https://django-treebeard.readthedocs.io/en/latest/ns_tree.html
    """

    node_order_by = ["topic"]

    class Meta:
        verbose_name = _("Set")
        verbose_name_plural = _("Sets")

    # TODO: add fk to studygroup to enable colaboration
    # TODO: refactor owner in "creator"
    creator = models.ForeignKey(
        User,
        help_text=_("Memo Set is owned by this user"),
        related_name="memosets",
        on_delete=models.CASCADE,
    )

    @property
    def owner(self):
        return self.creator

    topic = models.CharField(
        _("Topic"), help_text=_("Topic of Memo Set"), max_length=255
    )

    # TODO: pause-toogle
    # TODO: is-template => able to fork the set including tree and cards

    objects = MemoSetManager()

    def __str__(self):
        return "%s: %s (%s)" % (self._meta.verbose_name, self.topic, self.owner)

    @classmethod
    def get_rootlist_for(cls, user):
        return cls.get_root_nodes().filter(creator=user)

    def get_absolute_url(self):
        # Returns path to update-view
        return reverse("memoset_update_view", kwargs={"unique_id": self.unique_id})

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

    creator = models.ForeignKey(
        User,
        help_text=_("Memo Set is created by this user"),
        null=True,
        blank=True,
        related_name="memocards",
        on_delete=models.CASCADE,
    )

    memoset = models.ForeignKey(
        MemoSet,
        help_text=_("Memo Card is assigned to this set"),
        related_name="cards",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(
        _("Topic"),
        help_text=_("Topic of Memo Card"),
        max_length=255,
        null=True,
        blank=True,
    )
    # Card Content
    question_text = models.TextField(_("Question (Text)"), max_length=2000)
    answer_text = RichTextField(_("Answer (Text)"), max_length=2000)
    # TODO: audio-pair, image-pair

    objects = MemoCardManager()

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.topic)

    def get_absolute_url(self):
        # Returns path to update-view
        return reverse("memocard_update_view", kwargs={"unique_id": self.unique_id})

    def save(self, *args, **kwargs):
        return super(MemoCard, self).save(*args, **kwargs)


class MemoCardPerformanceManager(models.Manager):
    def get_random_object_for(self, user):
        # returns a random card performance object
        # TODO: exclude paused ones
        # return self.filter(owner=user).order_by("?").first()
        return self.for_user(user).active().get_random_from()

    def get_least_learned_object_for(self, user, limit=7):
        # returns one of the least learned card performance objects
        return random.choice(
            self.filter(owner=user, is_paused=False).order_by(
                "-priority", "learn_score"
            )[0:limit]
        )

    def get_least_recalled_object_for(self, user, limit=7):
        # returns one of the least learned card performance objects
        return random.choice(
            self.filter(owner=user, is_paused=False).order_by(
                "-priority", "recall_score"
            )[0:limit]
        )


LEARNING_PRIORITY = (
    (0, _("Low")),
    (1, _("Normal")),
    (2, _("High")),
)


class MemoCardPerformance(UUIDMixin, TimestampMixin, models.Model):
    """
    Card statistics & performance for a user on a card
    """

    class Meta:
        verbose_name = _("Card Performance")
        verbose_name_plural = _("Card Performances")
        unique_together = ["owner", "memocard"]

    owner = models.ForeignKey(
        User,
        help_text=_("User of the card performance"),
        related_name="memo_performances",
        on_delete=models.CASCADE,
    )
    memocard = models.ForeignKey(
        MemoCard,
        help_text=_("Card of the performance"),
        related_name="memo_performances",
        on_delete=models.CASCADE,
    )
    # Learning Settings
    learning_timeout = models.PositiveSmallIntegerField(
        _("Learning Timeout"), help_text=_("Learning Timeout in seconds"), default=120
    )
    is_paused = models.BooleanField(
        _("Paused"),
        help_text=_("Learning of associated card is paused."),
        default=False,
    )
    priority = models.PositiveSmallIntegerField(
        _("Learning Priority"),
        choices=LEARNING_PRIORITY,
        default=1,
    )

    # Data contains the memorization data for memorization statistics in json format.
    # See: https://github.com/rpkilby/jsonfield
    # Data Format:
    # { 'learning': [(datetime, outcome_int, duration_ms),...],
    #   'recalling': [(datetime, outcome_int, duration_ms),...]
    # }
    INITIAL_DATA = {"learning": [], "recalling": []}
    data = JSONField(_("Memorization Data"), default=INITIAL_DATA)

    recall_total_time = models.PositiveIntegerField(
        _("Total Recall Time"), help_text=_("Total time spend on testing"), default=0
    )
    recall_trials = models.PositiveIntegerField(
        _("Total Recall Trials"), help_text=_("Total recalls tried"), default=0
    )
    recall_score = models.DecimalField(
        _("Recall Score"),
        help_text=_("Recall Score of the Memo Card for the User"),
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    learn_total_time = models.PositiveIntegerField(
        _("Total Learn Time"), help_text=_("Total time spend on learning"), default=0
    )
    learn_trials = models.PositiveIntegerField(
        _("Total Learn Trials"), help_text=_("Total learnings tried"), default=0
    )
    learn_score = models.DecimalField(
        _("Learn Score"),
        help_text=_("Learn Score of the Memo Card for the User"),
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    objects = MemoCardPerformanceManager()

    def __str__(self):
        return _("%s's Performance on %s: %s") % (
            self.owner,
            self.memocard,
            self.recall_score,
        )

    @property
    def creator(self):
        # returns the owner as the creator (used in rules permission)
        return self.owner

    @property
    def is_active(self):
        # returns if it is paused or active
        if self.is_paused:
            return _("Paused")
        return _("Active")

    def get_absolute_url(self):
        # Returns path to update-view
        return reverse(
            "memocardperformance_update_view", kwargs={"unique_id": self.unique_id}
        )

    def set_initial_data(self):
        # Sets the data to initial value; .save() must be called separately
        self.data = self.INITIAL_DATA

    def recalculate_scores(self):
        #
        # TODO: Develop good algorithm what constitutes a learning/recall score
        #
        # TODO: Implement moving averagelater
        # N_LAST_TRIALS_FOR_SCORE = 7
        # Calculate Learning
        # learn_score = learn_total_outcome / N_LAST_TRIALS_FOR_SCORE
        learn_trials = 0
        learn_total_outcome = 0
        learn_total_time = 0
        for data_point in self.data["learning"]:
            learn_trials += 1
            learn_total_outcome += data_point[1]  # 0 or 1
            learn_total_time += data_point[2]
        self.learn_trials = learn_trials
        self.learn_total_time = learn_total_time
        if learn_trials > 0:
            self.learn_score = float(learn_total_outcome / learn_trials) * 100
        # Calculate Recalling
        # recall_score = learn_total_outcome / N_LAST_TRIALS_FOR_SCORE
        recall_trials = 0
        recall_total_outcome = 0
        recall_total_time = 0
        for data_point in self.data["recalling"]:
            recall_trials += 1
            recall_total_outcome += data_point[1] / 5.0  # 0 to 5 normalized to 0-1
            recall_total_time += data_point[2]
        self.recall_trials = recall_trials
        self.recall_total_time = recall_total_time
        if recall_trials > 0:
            self.recall_score = float(recall_total_outcome / recall_trials) * 100

    def add_learning_datapoint(self, outcome_int, duration_sec):
        # Adds a learning data point; .save() must be called separately
        timestamp = datetime.datetime.now()
        self.data["learning"].append((timestamp, outcome_int, duration_sec))

    def add_recalling_datapoint(self, outcome_int, duration_sec):
        # Adds a learning data point; .save() must be called separately
        timestamp = datetime.datetime.now()
        self.data["recalling"].append((timestamp, outcome_int, duration_sec))

    def save(self, *args, **kwargs):
        # Calculates all scores on save
        self.recalculate_scores()
        return super(MemoCardPerformance, self).save(*args, **kwargs)


#
# SIGNALS
#

# MEMO CARD CREATION (post save)
@receiver(post_save, sender=MemoCard)
def memocard_created(sender, instance, **kwargs):
    if kwargs["created"]:
        # Add MemoCardPerformance Instance with the MemoCard.creator as the owner
        performance_instance, created = MemoCardPerformance.objects.get_or_create(
            owner=instance.creator, memocard=instance
        )
