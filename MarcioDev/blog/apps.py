from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        # Liga o contador de tentativas de login falhadas (blog/seguranca.py).
        from . import seguranca  # noqa: F401
