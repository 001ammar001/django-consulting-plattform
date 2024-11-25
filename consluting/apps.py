from django.apps import AppConfig


class ConslutingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consluting'

    def ready(self) -> None:
        import consluting.signals.signals