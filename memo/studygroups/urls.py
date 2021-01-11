from django.urls import path

from memo.studygroups.views import (
    group_create_view,
    group_delete_view,
    group_detail_view,
    group_directory_view,
    group_invite_view,
    group_join_view,
    group_leave_view,
    group_list_view,
    group_update_view,
    membership_manage_view,
)

app_name = "studygroups"

urlpatterns = [
    # Main List View
    path(
        "",
        view=group_list_view,
        name="group_list_view",
    ),
    path(
        "directory/",
        view=group_directory_view,
        name="group_directory_view",
    ),
    path(
        "new/",
        view=group_create_view,
        name="group_create_view",
    ),
    # TODO:
    path(
        "welcome-to-<str:slug>",
        view=group_invite_view,  #
        name="group_invite_view",
    ),
    path(
        "join/<uuid:unique_id>",
        view=group_join_view,
        name="group_join_view",
    ),
    path(
        "leave/<uuid:unique_id>",
        view=group_leave_view,
        name="group_leave_view",
    ),
    path(
        "edit/<uuid:unique_id>",
        view=group_update_view,
        name="group_update_view",
    ),
    path(
        "delete/<uuid:unique_id>",
        view=group_delete_view,
        name="group_delete_view",
    ),
    path(
        "detail/<str:slug>",
        view=group_detail_view,
        name="group_detail_view",
    ),
    path(
        "manage/<uuid:unique_id>/<str:verb>",
        view=membership_manage_view,
        name="membership_manage_view",
    ),
]
