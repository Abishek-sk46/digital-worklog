from django.apps import AppConfig

class LogAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'log_app'

    def ready(self):
        import log_app.signals