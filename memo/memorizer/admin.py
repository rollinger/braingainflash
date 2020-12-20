from django.contrib import admin

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
class MemoSetAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "id",
        "parent",
        "topic",
        "owner",
        "is_template",
    )
    list_display_links = ("topic",)
    list_filter = ("is_template",)
    list_editable = ("is_template",)
    search_fields = ["topic"]
    autocomplete_fields = ["owner", "parent"]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "topic",
                    "owner",
                    "parent",
                    "is_template",
                )
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
