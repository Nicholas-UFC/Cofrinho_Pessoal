from django.contrib import admin
from django.http import HttpRequest

from whatsapp.models import SessaoConversa


@admin.register(SessaoConversa)
class SessaoConversaAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "estado", "usuario", "atualizado_em")
    list_filter = ("estado",)
    search_fields = ("chat_id",)
    readonly_fields = (
        "chat_id",
        "usuario",
        "estado",
        "dados_temporarios",
        "criado_em",
        "atualizado_em",
    )

    def has_add_permission(self, _request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, _request: HttpRequest, _obj: object = None
    ) -> bool:
        return False
