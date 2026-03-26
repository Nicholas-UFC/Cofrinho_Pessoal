from typing import ClassVar

from django.contrib.auth.models import User
from django.db import models

from financas.models import ManagerAuditavel


class SessaoConversa(models.Model):
    ESTADOS: ClassVar = [
        ("menu", "Menu Principal"),
        ("aguardando_valor_gasto", "Aguardando Valor do Gasto"),
        ("aguardando_categoria_gasto", "Aguardando Categoria do Gasto"),
        ("confirmando_gasto", "Confirmando Gasto"),
        ("aguardando_valor_entrada", "Aguardando Valor da Entrada"),
        ("aguardando_fonte_entrada", "Aguardando Fonte da Entrada"),
        ("confirmando_entrada", "Confirmando Entrada"),
    ]

    chat_id = models.CharField(max_length=100, unique=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessoes_conversa",
    )
    estado = models.CharField(
        max_length=50, choices=ESTADOS, default="menu"
    )
    dados_temporarios = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ManagerAuditavel()

    class Meta:
        verbose_name = "Sessão de Conversa"
        verbose_name_plural = "Sessões de Conversa"

    def __str__(self) -> str:
        return f"Sessão {self.chat_id} [{self.estado}]"
