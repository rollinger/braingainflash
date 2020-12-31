from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import MemoCard, MemoCardPerformance, MemoSet


class MemoCardInline(admin.TabularInline):
    model = MemoCard
    show_change_link = True
    ordering = ("-created_at",)
    extra = 1
    fields = ("topic",)
    # autocomplete_fields = ['source']
    # verbose_name_plural = "Predisposed by:"


@admin.register(MemoSet)
class MemoSetAdmin(TreeAdmin):
    form = movenodeform_factory(MemoSet)
    save_on_top = True
    list_display = ("topic", "creator", "studygroup")
    list_display_links = ("topic",)
    # list_filter = ("is_template",)
    # list_editable = ("is_template",)
    search_fields = ["topic", "creator"]
    autocomplete_fields = [
        "creator",
    ]
    readonly_fields = [
        "id",
        "unique_id",
    ]
    inlines = [
        MemoCardInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "topic",
                    "creator",
                )
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": (
                    "id",
                    "unique_id",
                    "_position",
                    # TODO: Turn the _ref_node_id in a autocomplete field...
                    "_ref_node_id",
                ),
            },
        ),
    )


class MemoCardPerformanceInline(admin.TabularInline):
    model = MemoCardPerformance
    fk_name = "memocard"
    show_change_link = True
    ordering = ("-created_at",)
    extra = 0
    fields = (
        "memocard",
        "owner",
        "recall_score",
        "learn_score",
    )
    readonly_fields = [
        # "memocard",
        # "owner",
        # "score",
    ]
    # autocomplete_fields = ['source']
    # verbose_name_plural = "Predisposed by:"


@admin.register(MemoCard)
class MemoCardAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "memoset",
        "topic",
        "creator",
    )
    list_display_links = ("topic",)
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
    ]
    search_fields = ["topic", "creator"]
    autocomplete_fields = ["memoset"]
    inlines = [
        MemoCardPerformanceInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "topic",
                    "memoset",
                    "creator",
                )
            },
        ),
        (
            "Card Data",
            {
                "classes": ("extrapretty",),
                "fields": (
                    "question_text",
                    "answer_text",
                ),
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": ("id", "unique_id", "created_at", "updated_at"),
            },
        ),
    )


@admin.register(MemoCardPerformance)
class MemoCardPerformanceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "id",
        "unique_id",
        "memocard",
        "owner",
        "recall_score",
        "learn_score",
        "learning_timeout",
        "is_paused",
        "priority",
    )
    list_display_links = ("memocard",)
    list_editable = (
        "learning_timeout",
        "is_paused",
        "priority",
    )
    list_filter = (
        "is_paused",
        "priority",
    )
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
        "data",
        "recall_score",
        "recall_trials",
        "recall_total_time",
        "learn_score",
        "learn_trials",
        "learn_total_time",
        "owner",
        "memocard",
        "memocard_question_text",
        "memocard_answer_text",
    ]
    autocomplete_fields = ["owner", "memocard"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("owner", "memocard"),
                    ("memocard_question_text", "memocard_answer_text"),
                    (
                        "learning_timeout",
                        "is_paused",
                        "priority",
                    ),
                )
            },
        ),
        (
            "Performance Data",
            {
                "classes": ("extrapretty",),
                "fields": (
                    "data",
                    (
                        "recall_score",
                        "recall_trials",
                        "recall_total_time",
                    ),
                    ("learn_score", "learn_trials", "learn_total_time"),
                ),
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": ("id", "unique_id", "created_at", "updated_at"),
            },
        ),
    )

    def model_str(self, obj):
        return str(obj)

    model_str.short_description = "Card Performance"

    def memocard_question_text(self, obj):
        return obj.memocard.question_text

    memocard_question_text.short_description = "Question"

    def memocard_answer_text(self, obj):
        return obj.memocard.answer_text

    memocard_answer_text.short_description = "Answer"

    actions = ["reset_data"]

    def reset_data(self, request, queryset):
        for obj in queryset:
            obj.set_initial_data()
            obj.save()

    reset_data.short_description = "Reset data to initial value"
