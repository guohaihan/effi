from django.apps import AppConfig


class DbmsConfig(AppConfig):
    name = 'dbms'

    def ready(self):
        import dbms.signals
