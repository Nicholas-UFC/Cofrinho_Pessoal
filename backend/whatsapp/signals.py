from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from financas.models import LogAuditoria
from whatsapp.models import SessaoConversa


def _extrair_detalhes(instancia: models.Model) -> dict:
    return {
        f.name: str(getattr(instancia, f.name))
        for f in instancia._meta.local_fields
    }


@receiver(post_save, sender=SessaoConversa)
def registrar_criacao_ou_atualizacao_sessao(
    sender: type,  # noqa: ARG001
    instance: SessaoConversa,
    created: bool,
    **_kwargs: object,
) -> None:
    acao = "criado" if created else "atualizado"
    LogAuditoria.objects.create(
        usuario=instance.usuario,
        acao=acao,
        modelo="SessaoConversa",
        objeto_id=instance.pk,
        detalhes=_extrair_detalhes(instance),
    )


@receiver(post_delete, sender=SessaoConversa)
def registrar_delecao_sessao(
    sender: type,  # noqa: ARG001
    instance: SessaoConversa,
    **_kwargs: object,
) -> None:
    LogAuditoria.objects.create(
        usuario=instance.usuario,
        acao="deletado",
        modelo="SessaoConversa",
        objeto_id=instance.pk,
        detalhes=_extrair_detalhes(instance),
    )
