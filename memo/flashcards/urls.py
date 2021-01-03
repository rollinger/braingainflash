from django.urls import path

from memo.flashcards.views import (
    card_create_view,
    card_delete_view,
    card_update_view,
    performance_update_view,
    topic_create_view,
)

app_name = "flashcards"

urlpatterns = [
    # Topic
    path(
        "group/<uuid:unique_group_id>/create-topic",
        view=topic_create_view,
        name="topic_create_view",
    ),
    # Cards
    path(
        "group/<uuid:unique_group_id>/create-card",
        view=card_create_view,
        name="card_create_view",
    ),
    # TODO
    path(
        "manage/card/<uuid:unique_id>/update",
        view=card_update_view,
        name="card_update_view",
    ),
    path(
        "manage/card/<uuid:unique_id>/delete",
        view=card_delete_view,
        name="card_delete_view",
    ),
    path(
        "manage/settings/<uuid:unique_id>/update",
        view=performance_update_view,
        name="performance_update_view",
    ),
]
