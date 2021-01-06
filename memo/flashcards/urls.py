from django.urls import path

from memo.flashcards.views import (  # performance_update_view, card_delete_view,    card_update_view,
    card_create_view,
    card_update_delete_view,
    test_cards_view,
    topic_create_view,
    topic_update_delete_view,
    train_cards_view,
)

app_name = "flashcards"

urlpatterns = [
    #
    # Topic
    #
    path(
        "group/<uuid:unique_group_id>/create-topic",
        view=topic_create_view,
        name="topic_create_view",
    ),
    path(  # Handles update and delete
        "manage/topic/<uuid:unique_id>/update",
        view=topic_update_delete_view,
        name="topic_update_delete_view",
    ),
    #
    # Cards
    #
    path(
        "group/<uuid:unique_group_id>/create-card",
        view=card_create_view,
        name="card_create_view",
    ),
    path(  # Handles update and delete
        "manage/card/<uuid:unique_id>/update",
        view=card_update_delete_view,
        name="card_update_delete_view",
    ),
    # Test & Train interface
    path(
        "train",
        view=train_cards_view,
        name="train_cards_view",
    ),
    path(
        "recall",
        view=test_cards_view,
        name="test_cards_view",
    ),
    # TODO / DELETE
    # path(
    #    "manage/settings/<uuid:unique_id>/update",
    #    view=performance_update_view,
    #    name="performance_update_view",
    # ),
]
