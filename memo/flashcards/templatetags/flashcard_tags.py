from ckeditor.widgets import CKEditorWidget
from django import template
from flashcards.forms import CardForm, PerformanceForm
from flashcards.models import Performance

register = template.Library()


@register.simple_tag()
def card_performance(user, card):
    # returns the card performance for this user or None
    return Performance.objects.filter(owner=user, card=card).first()


@register.inclusion_tag("flashcards/templatetags/_update_delete_card_modal.html")
def update_delete_card_modal(card):
    # Add initialized card_create_form for use in _create_card_modal.html
    card_update_delete_form = CardForm(instance=card)
    card_update_delete_form.fields["topic"].queryset = card.group.topics
    card_update_delete_form.fields["front_text"].widget = CKEditorWidget(
        attrs={"id": "%d_id_front_text" % (card.id)}
    )
    card_update_delete_form.fields["back_text"].widget = CKEditorWidget(
        attrs={"id": "%d_id_back_text" % (card.id)}
    )
    return {"card": card, "card_update_delete_form": card_update_delete_form}


@register.inclusion_tag("flashcards/templatetags/_update_performance_modal.html")
def update_performance_modal(performance):
    performance_form = PerformanceForm(instance=performance)
    return {"performance": performance, "performance_form": performance_form}
