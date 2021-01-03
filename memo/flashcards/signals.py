from django.db.models.signals import post_save
from django.dispatch import receiver
from flashcards.models import Card, Performance


# CARD CREATION (post save)
@receiver(post_save, sender=Card)
def card_created(sender, instance, **kwargs):
    if kwargs["created"]:
        # Add a Performance object for card and card creator
        print("instance")
        performance_object, created = Performance.objects.get_or_create(
            owner=instance.creator, card=instance
        )
