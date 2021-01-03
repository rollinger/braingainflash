import datetime
import random

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from studygroups.models import StudyGroup
from utils.abstract_models import TimestampMixin, UUIDMixin

User = get_user_model()


LEARNING_PRIORITIES = (
    ("low", _("Low")),
    ("normal", _("Normal")),
    ("high", _("High")),
)

# Data Format:
# { 'learning': [(datetime, outcome_int, duration_ms),...],
#   'recalling': [(datetime, outcome_int, duration_ms),...]
# }
INITIAL_PERFORMANCE_DATA = {"learning": [], "recalling": []}


class TopicManager(models.Manager):
    pass


class Topic(UUIDMixin, TimestampMixin, models.Model):
    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        unique_together = ["group", "title"]
        ordering = ("group", "title")

    group = models.ForeignKey(
        StudyGroup,
        help_text=_("Study group of the topic"),
        related_name="topics",
        on_delete=models.CASCADE,
    )

    title = models.CharField(_("Title"), help_text=_("Title of Topic"), max_length=255)

    objects = TopicManager()

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.title)

    def get_absolute_url(self):
        # Returns path to update-view
        # return reverse("memoset_update_view", kwargs={"unique_id": self.unique_id})
        pass

    def save(self, *args, **kwargs):
        return super(Topic, self).save(*args, **kwargs)


class CardManager(models.Manager):
    pass


class Card(UUIDMixin, TimestampMixin, models.Model):
    """
    A card consisting of a question answer pairs to be memorize
    """

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")
        unique_together = ["group", "front_text"]
        ordering = ("group", "-topic", "front_text")

    group = models.ForeignKey(
        StudyGroup,
        help_text=_("Card is assigned to this group"),
        related_name="cards",
        on_delete=models.CASCADE,
    )

    topic = models.ForeignKey(
        Topic,
        help_text=_("Card is grouped by this topic (optional)"),
        related_name="cards",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    creator = models.ForeignKey(
        User,
        help_text=_("Card is created by this user"),
        related_name="cards",
        on_delete=models.CASCADE,
    )

    #
    # Card Content
    #
    front_text = RichTextField(
        _("Frontside Text"), help_text=_("Usually the Question"), max_length=2000
    )
    back_text = RichTextField(
        _("Backside Text"), help_text=_("Usually the Answer"), max_length=2000
    )
    # TODO: automatic Google text-to-speech sync for front/back text
    # TODO: audio-pair, image-pair

    objects = CardManager()

    def __str__(self):
        return "%s: %s" % (self._meta.verbose_name, self.front_text)

    def get_absolute_url(self):
        # Returns path to update-view
        # return reverse("memocard_update_view", kwargs={"unique_id": self.unique_id})
        pass

    def save(self, *args, **kwargs):
        return super(Card, self).save(*args, **kwargs)


class PerformanceManager(models.Manager):
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


class Performance(UUIDMixin, TimestampMixin, models.Model):
    """
    Card statistics & performance for a user on a card
    """

    class Meta:
        verbose_name = _("Performance")
        verbose_name_plural = _("Performances")
        unique_together = ["owner", "card"]
        ordering = (
            "owner",
            "-recall_score",
        )

    owner = models.ForeignKey(
        User,
        help_text=_("User of the card performance"),
        related_name="memo_performances",
        on_delete=models.CASCADE,
    )
    card = models.ForeignKey(
        Card,
        help_text=_("Card of the performance"),
        related_name="memo_performances",
        on_delete=models.CASCADE,
    )
    #
    # Learning Settings
    #
    learn_timeout = models.PositiveSmallIntegerField(
        _("Learning Timeout"),
        help_text=_("Timeout in seconds for learning the card"),
        default=120,
    )
    recall_timeout = models.PositiveSmallIntegerField(
        _("Recalling Timeout"),
        help_text=_("Timeout in seconds for recalling the card"),
        default=120,
    )
    is_paused = models.BooleanField(
        _("Paused"),
        help_text=_("Learning of associated card is paused."),
        default=False,
    )
    priority = models.CharField(
        _("Learning Priority"),
        help_text=_("Default role of new member"),
        max_length=20,
        choices=LEARNING_PRIORITIES,
        default="normal",
    )

    # Data contains the memorization data for memorization statistics in json format.
    # See: https://github.com/rpkilby/jsonfield
    # Data Format:
    # { 'learning': [(datetime, outcome_int, duration_ms),...],
    #   'recalling': [(datetime, outcome_int, duration_ms),...]
    # }
    data = JSONField(_("Performance Data"), default=INITIAL_PERFORMANCE_DATA)

    recall_total_time = models.PositiveIntegerField(
        _("Total Recall Time"), help_text=_("Total time spend on testing"), default=0
    )
    recall_trials = models.PositiveIntegerField(
        _("Total Recall Trials"), help_text=_("Total recalls tried"), default=0
    )
    recall_score = models.DecimalField(
        _("Recall Score"),
        help_text=_("Recall Score of the Card for the User"),
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
        help_text=_("Learn Score of the Card for the User"),
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    objects = PerformanceManager()

    def __str__(self):
        return _("%s's Performance on %s: %s") % (
            self.owner,
            self.card,
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
        # return reverse("memocardperformance_update_view", kwargs={"unique_id": self.unique_id})
        pass

    def set_initial_data(self):
        # Sets the data to initial value; .save() must be called separately
        self.data = INITIAL_PERFORMANCE_DATA

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
        return super(Performance, self).save(*args, **kwargs)
