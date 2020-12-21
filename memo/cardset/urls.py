from django.urls import path

from memo.cardset.views import (
    memocard_detail_view,
    memoset_detail_view,
    memoset_root_list_view,
)

app_name = "cardset"

urlpatterns = [
    # Sets
    path(
        "manage/set/root/list",
        view=memoset_root_list_view,
        name="memoset.views.rootlist",
    ),
    path(
        "manage/set/<str:unique_id>/detail",
        view=memoset_detail_view,
        name="memoset.views.detail",
    ),
    # Cards
    path(
        "manage/card/<str:unique_id>/detail",
        view=memocard_detail_view,
        name="memoset.views.detail",
    ),
]
