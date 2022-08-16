from django.apps import AppConfig


class UserdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'UserData'
    def ready(self):
        import UserData.Signals