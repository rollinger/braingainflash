from django import template
from flashcards.models import Performance

register = template.Library()


@register.simple_tag()
def card_performance(user, card):
    # returns the card performance for this user or None
    return Performance.objects.filter(owner=user, card=card).first()
