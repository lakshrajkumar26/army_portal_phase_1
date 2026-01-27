from django.apps import AppConfig


class ReferenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reference'

    def ready(self):
        # import the signal receiver so it's registered
        from . import signals  # noqa: F401
