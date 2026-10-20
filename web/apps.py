from django.apps import AppConfig


class WebConfig(AppConfig):
    name = "web"

    def ready(self):
        from web import auth  # noqa: F401  registra las senales de login
