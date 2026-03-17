from typing import ClassVar

from django.contrib import admin

from financas.models import Categoria, Entrada, Fonte, Gasto


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
