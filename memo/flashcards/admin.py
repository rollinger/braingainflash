from django.contrib import admin

from .models import Card, Performance, Topic


class CardInline(admin.TabularInline):
    model = Card
    show_change_link = True
    ordering = ("-created_at",)
    extra = 1
    fields = ("front_text", "group", "creator")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "group",
        "title",
    )
    list_display_links = ("title",)
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
    ]
    search_fields = ["group", "title"]
    autocomplete_fields = ["group"]
    inlines = [
        CardInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "group",
                )
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


class PerformanceInline(admin.TabularInline):
    model = Performance
    fk_name = "card"
    show_change_link = True
    ordering = ("-created_at",)
    extra = 0
    fields = (
        "owner",
        "recall_score",
        "learn_score",
        "is_paused",
        "priority",
    )
    readonly_fields = [
        # "card",
        # "owner",
        # "score",
    ]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "front_text",
        "group",
        "topic",
        "creator",
    )
    list_display_links = ("front_text",)
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
    ]
    search_fields = ["front_text", "back_text", "topic", "group"]
    autocomplete_fields = ["group", "creator"]
    inlines = [PerformanceInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "group",
                    "topic",
                )
            },
        ),
        (
            "Card Data",
            {
                "classes": ("extrapretty",),
                "fields": (
                    "front_text",
                    "back_text",
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


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "owner",
        "card",
        "recall_score",
        "learn_score",
        "is_paused",
        "priority",
    )
    list_display_links = ("card",)
    list_editable = (
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
        "card",
        "card_front_text",
        "card_back_text",
    ]
    autocomplete_fields = ["owner", "card"]
    actions = ["reset_data"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("owner", "card"),
                    ("card_front_text", "card_back_text"),
                    (
                        "learn_timeout",
                        "recall_timeout",
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

    def card_front_text(self, obj):
        return obj.card.front_text

    card_front_text.short_description = "Front Side"

    def card_back_text(self, obj):
        return obj.card.back_text

    card_back_text.short_description = "Back Side"

    def reset_data(self, request, queryset):
        for obj in queryset:
            obj.set_initial_data()
            obj.save()

    reset_data.short_description = "Reset data to initial value"
