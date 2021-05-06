from django.contrib import admin
from django.contrib.auth import get_user_model
from shareholder.models import Assignment, Review, Task

User = get_user_model()


class AssignmentsInline(admin.TabularInline):
    model = Assignment
    fk_name = "task"
    ordering = ("-workload_share",)
    autocomplete_fields = ["collaborator"]
    extra = 0
    fields = ("collaborator", "workload_share", "notes")


class ReviewInline(admin.StackedInline):
    model = Review
    fk_name = "task"
    ordering = ("-rating",)
    autocomplete_fields = ["reviewer"]
    readonly_fields = ("workload", "start_date", "closing_date")
    extra = 0
    fields = (
        ("reviewer", "rating"),
        "notes",
        ("workload", "start_date", "closing_date"),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    save_on_top = True
    date_hierarchy = "start_date"
    ordering = ("-closing_date",)
    list_display = (
        "title",
        "status",
        "start_date",
        "closing_date",
        "workload",
        "get_assigned_shareholder",
    )
    list_editable = ("status",)
    list_display_links = ("title",)
    list_filter = ("status",)
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
        # "creator",
    ]
    search_fields = [
        "title",
        "description",
    ]
    autocomplete_fields = ["creator"]
    inlines = [
        AssignmentsInline,
        ReviewInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "title",
                        "status",
                    ),
                    (
                        "start_date",
                        "closing_date",
                        "workload",
                    ),
                    "description",
                    (
                        "feature_branch",
                        "jira_url",
                    ),
                )
            },
        ),
        (
            "Fulfillment Report",
            {
                "classes": ("collapsible",),
                "fields": (
                    "report_text",
                    "report_file",
                ),
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": ("id", "unique_id", "creator", "created_at", "updated_at"),
            },
        ),
    )

    def get_assigned_shareholder(self, obj):
        # PR-060421: display assignments usernames
        workforce = ""
        for assignment in obj.assignments.all():
            workforce += assignment.collaborator.username + ", "
        return workforce  # trip_tags(obj.card.front_text)[:30]

    get_assigned_shareholder.short_description = "Workforce"

    def changelist_view(self, request, extra_context=None):
        # PR-060421: Make default list filter set to 'active' per default
        # See: https://stackoverflow.com/a/3783930/2257930
        test = request.META["HTTP_REFERER"].split(request.META["PATH_INFO"])
        if test[-1] and not test[-1].startswith("?"):
            if "status__exact" not in request.GET:
                q = request.GET.copy()
                q["status__exact"] = "pending"
                request.GET = q
                request.META["QUERY_STRING"] = request.GET.urlencode()
        return super(TaskAdmin, self).changelist_view(
            request, extra_context=extra_context
        )
