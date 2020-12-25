from django.urls import path

from memo.cardset.views import (  # memocard_detail_view,; memoset_detail_view,; CRUD Views; Gain Views
    memocard_create_view,
    memocard_delete_view,
    memocard_update_view,
    memoset_create_view,
    memoset_delete_view,
    memoset_root_list_view,
    memoset_update_view,
    train_gain_view,
)

app_name = "cardset"

urlpatterns = [
    # Main List View
    path(
        "manage/set/root/list",
        view=memoset_root_list_view,
        name="memoset_root_list_view",
    ),
    # MemoSet CRUD operations
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
    # Current Workpoint: Add Basic Workflow MemoCard CRUD to frontend
    # TODO: ...
    path(
        "manage/card/<uuid:unique_id>/create",
        view=memocard_create_view,
        name="memocard_create_view",
    ),
    path(
        "manage/card/<uuid:unique_id>/update",
        view=memocard_update_view,
        name="memocard_update_view",
    ),
    path(
        "manage/card/<uuid:unique_id>/delete",
        view=memocard_delete_view,
        name="memocard_delete_view",
    ),
    path(
        "train/gain",
        view=train_gain_view,
        name="train_gain_view",
    ),
]
