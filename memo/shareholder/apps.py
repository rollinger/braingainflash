from django.apps import AppConfig


class ShareholderConfig(AppConfig):
    name = "shareholder"
    verbose_name = "Shareholder"

    def ready(self):
        try:
            import memo.shareholder.signals  # noqa F401
        except ImportError:
            pass
