from django.apps import AppConfig


class FinancasConfig(AppConfig):
    name = "financas"

    def ready(self) -> None:
        import financas.signals  # noqa: F401, PLC0415
