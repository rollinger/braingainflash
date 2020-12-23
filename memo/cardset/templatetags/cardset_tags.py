from cardset.models import MemoCardPerformance
from django import template

register = template.Library()


@register.simple_tag()
def card_performance(user, card):
    # returns the card performance for this user or None
    return MemoCardPerformance.objects.filter(owner=user, memocard=card).first()
