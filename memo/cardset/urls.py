from django.urls import path

from memo.cardset.views import (  # memocard_detail_view,; memoset_detail_view,
    memoset_create_view,
    memoset_delete_view,
    memoset_root_list_view,
    memoset_update_view,
)

app_name = "cardset"

urlpatterns = [
    # Sets
    path(
        "manage/set/root/list",
        view=memoset_root_list_view,
        name="memoset_root_list_view",
    ),
    # Current Workpoint: CUD for Set
    path(
        "manage/set/create",
        view=memoset_create_view,
        name="memoset_create_view",
    ),
    path(
        "manage/set/<uuid:unique_id>/create",
        view=memoset_create_view,
        name="memoset_create_view",
    ),
    path(
        "manage/set/<uuid:unique_id>/update",
        view=memoset_update_view,
        name="memoset_update_view",
    ),
    path(
        "manage/set/<uuid:unique_id>/delete",
        view=memoset_delete_view,
        name="memoset_delete_view",
    ),
]

"""



path(
    "manage/set/<uuid:unique_id>/detail",
    view=memoset_detail_view,
    name="memoset.views.detail",
),
# Cards
path(
    "manage/card/<uuid:unique_id>/detail",
    view=memocard_detail_view,
    name="memoset.views.detail",
),
"""
