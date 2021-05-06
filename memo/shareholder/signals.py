# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.contrib.auth import get_user_model
from shareholder.models import SHAREHOLDER_PERM_GROUP, Dividends  # IncomePeriod

User = get_user_model()


# IncomePeriod CREATION (post save)
# @receiver(post_save, sender=IncomePeriod)
def income_period_created(sender, instance, **kwargs):
    if kwargs["created"]:
        for shareholder in User.objects.filter(groups_in=SHAREHOLDER_PERM_GROUP):
            d, c = Dividends.objects.get_or_create(
                shareholder=shareholder, income_period=instance
            )


# Dividends CREATION (post save)
# @receiver(post_save, sender=Dividends)
def dividend_created(sender, instance, **kwargs):
    if kwargs["created"]:
        for task in instance.shareholder.assignments.filter(""):
            pass
        for review in instance.shareholder.reviews_made.all():
            pass
