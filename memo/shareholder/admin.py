from django.contrib import admin
from shareholder.models import Assignment, Review, Task


class AssignmentsInline(admin.TabularInline):
    model = Assignment
    fk_name = "task"
    ordering = ("-workload_share",)
    autocomplete_fields = ["collaborator"]
    extra = 1
    fields = ("collaborator", "workload_share", "notes")


class ReviewInline(admin.StackedInline):
    model = Review
    fk_name = "task"
    ordering = ("-rating",)
    readonly_fields = ("workload", "start_date", "closing_date")
    extra = 1
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
    )
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
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": ("id", "unique_id", "creator", "created_at", "updated_at"),
            },
        ),
    )
