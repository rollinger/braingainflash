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
    list_display = (
        "topic",
        "creator",
    )
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
        "score",
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
