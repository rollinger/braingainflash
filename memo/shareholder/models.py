from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from utils.abstract_models import TimestampMixin, UUIDMixin

User = get_user_model()


TASK_STATUS = (
    ("proposed", _("Task is proposed")),  # shareholder can propose tasks
    ("active", _("Task is active")),  # project lead can accept tasks
    ("pending", _("Task is pending")),  # start_date makes task pending
    ("review", _("Task is under review")),  # closing_date puts task to review
    ("completed", _("Task is completed")),  # project lead can set tasks as completed
    ("failed", _("Task is failed")),  # project lead can set tasks as failed
)
REVIEW_RATING = (
    ("failed", _("Task completion failed")),  # Fail
    ("buggy", _("Task completion is buggy")),  # Bugs
    ("completed", _("Task completion is done")),  # Done
    ("well", _("Task completion well done")),  # Good
    ("super", _("Task completion superbly done")),  # Super
)
TASK_STANDARD_WORKLOAD = 1.0
REVIEW_RATING_STANDARD_WORKLOAD = 0.5


class Task(UUIDMixin, TimestampMixin, models.Model):
    """
    A task for a shareholder
    """

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ("-start_date", "workload")

    creator = models.ForeignKey(
        User,
        help_text=_("Creator of the task"),
        related_name="created_tasks",
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        _("Status"),
        help_text=_("Status of the task"),
        max_length=20,
        choices=TASK_STATUS,
        default="proposed",
    )

    workload = models.DecimalField(
        "Workload in hour shares",
        max_digits=4,
        decimal_places=2,
        default=TASK_STANDARD_WORKLOAD,
    )

    start_date = models.DateTimeField(_("Task's Start Date"), blank=True)
    closing_date = models.DateTimeField(_("Task's Deadline"), blank=True)

    title = models.CharField(
        _("Short Summary"),
        default="Task: ...",
        max_length=255,
    )

    description = models.TextField(
        _("Description"), help_text=_("Task's description and goals"), max_length=5000
    )

    feature_branch = models.CharField(
        _("GIT feature branch name"),
        max_length=255,
    )

    jira_url = models.URLField(_("URL to JIRA Task"), blank=True)


class Assignment(UUIDMixin, TimestampMixin, models.Model):
    """
    An assignment of a shareholder to a task
    """

    class Meta:
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")
        ordering = ("-workload_share",)

    task = models.ForeignKey(
        Task,
        help_text=_("Assignment Task"),
        related_name="assignments",
        on_delete=models.CASCADE,
    )

    collaborator = models.ForeignKey(
        User,
        help_text=_("Assignment Collaborator"),
        related_name="assignments",
        on_delete=models.CASCADE,
    )

    workload_share = models.PositiveSmallIntegerField(
        _("Workload Share of the collaborator"),
        help_text=_("Two collaborators with 100% would get 50% each."),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        default=100,
    )

    notes = models.TextField(
        _("Assignment Notes"),
        help_text=_("Information of the collaborators role and responsibilities"),
        max_length=1000,
    )


class Review(UUIDMixin, TimestampMixin, models.Model):
    """
    A review by a shareholder of a whole task
    """

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        # ordering = ("-is_main_user_group", "name")

    task = models.ForeignKey(
        Task,
        help_text=_("Review of Task"),
        related_name="reviews",
        on_delete=models.CASCADE,
    )

    reviewer = models.ForeignKey(
        User,
        help_text=_("Reviewer of the Task"),
        related_name="reviews_made",
        on_delete=models.CASCADE,
    )

    rating = models.CharField(
        _("Rating"),
        help_text=_("Reviewers assessment"),
        max_length=20,
        choices=REVIEW_RATING,
        default="done",
    )

    notes = models.TextField(
        _("Assignment Notes"),
        help_text=_("Information of the collaborators role and responsibilities"),
        max_length=1000,
    )

    workload = models.DecimalField(
        "Workload assigned for rating",
        max_digits=4,
        decimal_places=2,
        default=REVIEW_RATING_STANDARD_WORKLOAD,
    )

    @property
    def start_date(self):
        if self.task:
            return self.task.start_date
        return _("Not set")

    @property
    def closing_date(self):
        if self.task:
            return self.task.closing_date + timedelta(days=1)
        return _("Not set")
