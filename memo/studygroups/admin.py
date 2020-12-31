from django.contrib import admin

from .models import Membership, StudyGroup


class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = "group"
    ordering = ("-role",)
    extra = 0
    fields = (
        "member",
        "role",
        "created_at",
        "updated_at",
    )
    readonly_fields = [
        "member",
        "created_at",
        "updated_at",
    ]
    # autocomplete_fields = ['source']
    # verbose_name_plural = "Predisposed by:"


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "name",
        "slug",
        "join_mode",
        "is_main_user_group",
    )
    list_display_links = ("name",)
    list_filter = ("join_mode", "is_main_user_group")
    readonly_fields = [
        "id",
        "unique_id",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
    ]
    prepopulated_fields = {"slug": ("name",)}
    # autocomplete_fields = ["memoset"]
    inlines = [
        MembershipInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "name",
                        "slug",
                    ),
                    "description",
                )
            },
        ),
        (
            "Group Settings",
            {
                "classes": ("extrapretty",),
                "fields": (("join_mode", "new_member_role"),),
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
