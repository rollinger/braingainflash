from django.apps import AppConfig


class StudyGroupsConfig(AppConfig):
    name = "studygroups"
    verbose_name = "Study Groups"

    def ready(self):
        try:
            import memo.studygroups.signals  # noqa F401
        except ImportError:
            pass
