from django.apps import AppConfig


class DealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deals'

    def ready(self):
        # ensure signals are imported when app is ready
        import deals.signals  # noqa: F401
