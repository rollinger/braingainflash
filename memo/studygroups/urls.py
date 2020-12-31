from django.urls import path

from memo.studygroups.views import (
    group_create_view,
    group_directory_view,
    group_join_view,
    group_list_view,
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
    path(
        "join/<uuid:unique_id>",
        view=group_join_view,
        name="group_join_view",
    ),
]
