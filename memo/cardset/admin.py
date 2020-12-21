from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import MemoCard, MemoSet


class MemoCardInline(admin.TabularInline):
    model = MemoCard
    show_change_link = True
    ordering = ("-score",)
    extra = 1
    fields = (
        "score",
        "topic",
    )
    # autocomplete_fields = ['source']
    # verbose_name_plural = "Predisposed by:"


@admin.register(MemoSet)
class MemoSetAdmin(TreeAdmin):
    form = movenodeform_factory(MemoSet)
    save_on_top = True
    list_display = (
        "topic",
        "owner",
    )
    list_display_links = ("topic",)
    # list_filter = ("is_template",)
    # list_editable = ("is_template",)
    search_fields = ["topic"]
    autocomplete_fields = [
        "owner",
    ]
    readonly_fields = [
        "id",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "topic",
                    "owner",
                )
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": (
                    "id",
                    "_position",
                    "_ref_node_id",
                ),
            },
        ),
    )
    inlines = [
        MemoCardInline,
    ]


@admin.register(MemoCard)
class MemoCardAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "id",
        "memoset",
        "topic",
        "score",
        "get_owner",
    )
    list_display_links = ("topic",)
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["memoset"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "topic",
                    "memoset",
                    "score",
                )  # 'get_owner',
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
            "Training Data",
            {
                "classes": ("extrapretty",),
                "fields": ("data",),
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapsible",),
                "fields": ("id", "created_at", "updated_at"),
            },
        ),
    )

    def get_owner(self, obj):
        return obj.memoset.owner

    get_owner.admin_order_field = "owner"  # Allows column order sorting
    get_owner.short_description = "Owner"  # Renames column head
