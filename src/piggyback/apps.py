from django.apps import AppConfig


class PiggybackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "piggyback"
    verbose_name = "Piggyback Occasion Cards"

    def ready(self):
        from piggyback import signals  # noqa: F401
