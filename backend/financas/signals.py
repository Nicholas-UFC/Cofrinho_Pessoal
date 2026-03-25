from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from financas.models import Categoria, Entrada, Fonte, Gasto, LogAuditoria


def _extrair_detalhes(instancia: models.Model) -> dict:
    return {
        f.name: str(getattr(instancia, f.name))
        for f in instancia._meta.local_fields
    }


@receiver(post_save, sender=Gasto)
@receiver(post_save, sender=Entrada)
@receiver(post_save, sender=Categoria)
@receiver(post_save, sender=Fonte)
def registrar_criacao_ou_atualizacao(
    sender: type,
    instance: models.Model,
    created: bool,
    **_kwargs: object,
) -> None:
    acao = "criado" if created else "atualizado"
    LogAuditoria.objects.create(
        usuario=instance.usuario,  # type: ignore[attr-defined]
        acao=acao,
        modelo=sender.__name__,
        objeto_id=instance.pk,
        detalhes=_extrair_detalhes(instance),
    )


@receiver(post_delete, sender=Gasto)
@receiver(post_delete, sender=Entrada)
@receiver(post_delete, sender=Categoria)
@receiver(post_delete, sender=Fonte)
def registrar_delecao(
    sender: type,
    instance: models.Model,
    **_kwargs: object,
) -> None:
    LogAuditoria.objects.create(
        usuario=instance.usuario,  # type: ignore[attr-defined]
        acao="deletado",
        modelo=sender.__name__,
        objeto_id=instance.pk,
        detalhes=_extrair_detalhes(instance),
    )


@receiver(post_save, sender=User)
def registrar_criacao_ou_atualizacao_usuario(
    sender: type,  # noqa: ARG001
    instance: User,
    created: bool,
    **_kwargs: object,
) -> None:
    acao = "criado" if created else "atualizado"
    LogAuditoria.objects.create(
        usuario=None,
        acao=acao,
        modelo="User",
        objeto_id=instance.pk,
        detalhes={
            "username": instance.username,
            "email": instance.email,
            "is_active": str(instance.is_active),
        },
    )


@receiver(post_delete, sender=User)
def registrar_delecao_usuario(
    sender: type,  # noqa: ARG001
    instance: User,
    **_kwargs: object,
) -> None:
    LogAuditoria.objects.create(
        usuario=None,
        acao="deletado",
        modelo="User",
        objeto_id=instance.pk,
        detalhes={"username": instance.username, "email": instance.email},
    )
