from typing import ClassVar

from django.contrib import admin

from financas.models import (
    Categoria,
    Entrada,
    Fonte,
    Gasto,
    LogAcesso,
    LogAuditoria,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display: ClassVar = ["nome", "usuario", "criado_em"]
    search_fields: ClassVar = ["nome", "usuario__username"]
    list_filter: ClassVar = ["usuario"]
    readonly_fields: ClassVar = ["id", "criado_em"]
    ordering: ClassVar = ["nome"]


@admin.register(Fonte)
class FonteAdmin(admin.ModelAdmin):
    list_display: ClassVar = ["nome", "usuario", "criado_em"]
    search_fields: ClassVar = ["nome", "usuario__username"]
    list_filter: ClassVar = ["usuario"]
    readonly_fields: ClassVar = ["id", "criado_em"]
    ordering: ClassVar = ["nome"]


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display: ClassVar = [
        "descricao",
        "valor",
        "categoria",
        "usuario",
        "data",
    ]
    search_fields: ClassVar = ["descricao", "usuario__username"]
    list_filter: ClassVar = ["categoria", "usuario", "data"]
    readonly_fields: ClassVar = ["id", "criado_em"]
    ordering: ClassVar = ["-data"]


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display: ClassVar = [
        "descricao",
        "valor",
        "fonte",
        "usuario",
        "data",
    ]
    search_fields: ClassVar = ["descricao", "usuario__username"]
    list_filter: ClassVar = ["fonte", "usuario", "data"]
    readonly_fields: ClassVar = ["id", "criado_em"]
    ordering: ClassVar = ["-data"]


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display: ClassVar = [
        "acao",
        "modelo",
        "objeto_id",
        "usuario",
        "criado_em",
    ]
    search_fields: ClassVar = ["modelo", "usuario__username"]
    list_filter: ClassVar = ["acao", "modelo", "usuario"]
    readonly_fields: ClassVar = [
        "acao",
        "modelo",
        "objeto_id",
        "usuario",
        "detalhes",
        "criado_em",
    ]
    ordering: ClassVar = ["-criado_em"]

    def has_add_permission(self, _request: object) -> bool:
        return False

    def has_change_permission(
        self, _request: object, _obj: object = None
    ) -> bool:
        return False


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display: ClassVar = [
        "metodo",
        "endpoint",
        "status_code",
        "origem",
        "dispositivo",
        "usuario",
        "ip",
        "duracao_ms",
        "criado_em",
    ]
    search_fields: ClassVar = ["endpoint", "ip", "usuario__username"]
    list_filter: ClassVar = ["metodo", "origem", "dispositivo", "status_code"]
    readonly_fields: ClassVar = [
        "usuario",
        "metodo",
        "endpoint",
        "status_code",
        "origem",
        "ip",
        "user_agent",
        "dispositivo",
        "duracao_ms",
        "criado_em",
    ]
    ordering: ClassVar = ["-criado_em"]

    def has_add_permission(self, _request: object) -> bool:
        return False

    def has_change_permission(
        self, _request: object, _obj: object = None
    ) -> bool:
        return False
