from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from utils.abstract_models import TimestampMixin, UUIDMixin

User = get_user_model()

SHAREHOLDER_PERM_GROUP = "Shareholder"
PROJECT_LEAD_PERM_GROUP = "Project Lead"

TASK_STATUS = (
    ("proposed", _("Task is proposed")),  # shareholder can propose tasks
    ("active", _("Task is active")),  # project lead can accept tasks
    ("working", _("Task is being build")),  # start_date makes task pending
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
        limit_choices_to={"groups__name": SHAREHOLDER_PERM_GROUP},
    )

    status = models.CharField(
        _("Status"),
        help_text=_("Status of the task"),
        max_length=20,
        choices=TASK_STATUS,
        default="proposed",
    )

    workload = models.DecimalField(
        "Workload shares",
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
        _("GIT feature branch name"), max_length=255, blank=True
    )

    jira_url = models.URLField(_("URL to JIRA Task"), blank=True)

    report_text = models.TextField(
        _("Report"),
        help_text=_("Report of the task's fulfillment."),
        max_length=5000,
        null=True,
        blank=True,
    )

    report_file = models.FileField(
        _("Report File"),
        help_text=_("File upload for report of the task's fulfillment."),
        upload_to="shareholder/task/reports/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s" % (self.title)


class Assignment(UUIDMixin, TimestampMixin, models.Model):
    """
    An assignment of a shareholder to a task
    """

    class Meta:
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")
        ordering = ("-workload_share",)
        unique_together = (
            "task",
            "collaborator",
        )

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
        limit_choices_to={"groups__name": SHAREHOLDER_PERM_GROUP},
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
        default="Task Lead",
        max_length=1000,
    )

    def __str__(self):
        return _("%s working on %s") % (self.collaborator, self.task.title)


class Review(UUIDMixin, TimestampMixin, models.Model):
    """
    A review by a shareholder of a whole task
    """

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        # ordering = ("-is_main_user_group", "name")
        unique_together = (
            "task",
            "reviewer",
        )

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
        limit_choices_to={"groups__name": SHAREHOLDER_PERM_GROUP},
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

    def __str__(self):
        return _("%s reviewed %s with %s") % (
            self.reviewer,
            self.task.title,
            self.rating,
        )


MONTH_CHOICE = (
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("Juli")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December")),
)


class IncomePeriod(UUIDMixin, TimestampMixin, models.Model):
    class Meta:
        verbose_name = _("Income Period")
        verbose_name_plural = _("Income Periods")
        ordering = ("-year", "-month")
        unique_together = (
            "month",
            "year",
        )

    year = models.PositiveSmallIntegerField(
        _("Year"), help_text=_("The year the surplus was generated"), default=2021
    )

    month = models.PositiveSmallIntegerField(
        _("Month"),
        help_text=_("The month the surplus was generated"),
        choices=MONTH_CHOICE,
    )

    surplus_total = models.DecimalField(
        _("Total Surplus €"),
        max_digits=12,
        decimal_places=2,
        default=0.0,
    )

    total_shares = models.DecimalField(
        _("Total Shares at reporting time"),
        max_digits=12,
        decimal_places=2,
        default=0.0,
    )


class Dividends(UUIDMixin, TimestampMixin, models.Model):
    class Meta:
        verbose_name = _("Dividends")
        verbose_name_plural = _("Dividends")
        ordering = ("-income_period", "-shareholder")
        unique_together = (
            "shareholder",
            "income_period",
        )

    shareholder = models.ForeignKey(
        User,
        help_text=_("Shareholder receiving the dividends"),
        related_name="dividends",
        on_delete=models.CASCADE,
        limit_choices_to={"groups__name": SHAREHOLDER_PERM_GROUP},
    )

    income_period = models.ForeignKey(
        IncomePeriod,
        help_text=_("Income Period the dividend relates to"),
        related_name="shares",
        on_delete=models.CASCADE,
    )

    task_share = models.DecimalField(
        _("Total Share Hours for Tasks"),
        max_digits=12,
        decimal_places=2,
        default=0.0,
    )

    review_share = models.DecimalField(
        _("Total Share Hours for Reviews"),
        max_digits=12,
        decimal_places=2,
        default=0.0,
    )

    amount = models.DecimalField(
        _("Dividend Amount €"),
        max_digits=12,
        decimal_places=2,
        default=0.0,
    )
