from django.apps import AppConfig


class FlashCardsConfig(AppConfig):
    name = "flashcards"
    verbose_name = "Flash Cards"

    def ready(self):
        try:
            import memo.flashcards.signals  # noqa F401
        except ImportError:
            pass
