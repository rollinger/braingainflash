from django.db.models.signals import post_save
from django.dispatch import receiver
from flashcards.models import Card, Performance


# CARD CREATION (post save)
@receiver(post_save, sender=Card)
def card_created(sender, instance, **kwargs):
    if kwargs["created"]:
        # Adds a Performance object for card and every group member
        for membership in instance.group.memberships.all():
            p, c = Performance.objects.get_or_create(
                owner=membership.member, card=instance
            )
