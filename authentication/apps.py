from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        import authentication.signals
        from utils.cron_jobs import start
        start()
