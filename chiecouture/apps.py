from django.apps import AppConfig

class ChiecoutureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chiecouture'

    def ready(self):
        import chiecouture.signals
