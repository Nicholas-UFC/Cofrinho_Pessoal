import hashlib
import json
from typing import ClassVar

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from financas.validators import validar_valor_positivo

# Campos que nunca devem ser alterados após a criação do registro.
_CAMPOS_IMUTAVEIS = {"id", "criado_em"}


# QuerySet que audita operações em massa (delete e update).
class QuerySetAuditavel(models.QuerySet):
    def delete(self, *args: object, **kwargs: object) -> tuple:
        from financas.models import LogAuditoria  # noqa: PLC0415

        ids = list(self.values_list("pk", flat=True))
        modelo = self.model.__name__
        for objeto_id in ids:
            LogAuditoria.objects.create(
                usuario=None,
                acao="bulk_deletado",
                modelo=modelo,
                objeto_id=objeto_id,
                detalhes={"ids_afetados": ids},
            )
        return super().delete(*args, **kwargs)

    def update(self, **kwargs: object) -> int:
        from financas.models import LogAuditoria  # noqa: PLC0415

        ids = list(self.values_list("pk", flat=True))
        modelo = self.model.__name__
        campos_alterados = {k: str(v) for k, v in kwargs.items()}
        for objeto_id in ids:
            LogAuditoria.objects.create(
                usuario=None,
                acao="bulk_atualizado",
                modelo=modelo,
                objeto_id=objeto_id,
                detalhes={"ids_afetados": ids, "campos": campos_alterados},
            )
        return super().update(**kwargs)


class ManagerAuditavel(models.Manager):
    def get_queryset(self) -> QuerySetAuditavel:
        return QuerySetAuditavel(self.model, using=self._db)


# Mixin reutilizável que protege campos imutáveis em qualquer UPDATE.
# Em vez de sobrescrever save() em cada model, basta herdar deste mixin.
class CamposImutaveisMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args: object, **kwargs: object) -> None:
        # Em updates, limita os campos gravados para proteger
        # campos imutáveis (id, criado_em) de alteração acidental.
        if self.pk and "update_fields" not in kwargs:
            updatable = [
                f.name
                for f in self._meta.local_fields
                if f.name not in _CAMPOS_IMUTAVEIS
            ]
            kwargs["update_fields"] = updatable
        super().save(*args, **kwargs)


# Tabela de categorias de gastos (ex: Alimentação, Transporte).
# Usada como chave estrangeira em Gasto.
class Categoria(CamposImutaveisMixin):
    # Cada usuário pode ter suas próprias categorias.
    # Dois usuários diferentes podem ter o mesmo nome de categoria.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categorias",
    )
    nome = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    objects = ManagerAuditavel()

    class Meta:
        ordering: ClassVar = ["nome"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        # Nome único por usuário (não globalmente).
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["usuario", "nome"],
                name="categoria_nome_unico_por_usuario",
            )
        ]

    def __str__(self) -> str:
        return self.nome


# Tabela de fontes de renda (ex: Salário, Freelance).
# Usada como chave estrangeira em Entrada.
class Fonte(CamposImutaveisMixin):
    # Cada usuário pode ter suas próprias fontes.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fontes",
    )
    nome = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    objects = ManagerAuditavel()

    class Meta:
        ordering: ClassVar = ["nome"]
        verbose_name = "Fonte"
        verbose_name_plural = "Fontes"
        # Nome único por usuário (não globalmente).
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["usuario", "nome"],
                name="fonte_nome_unico_por_usuario",
            )
        ]

    def __str__(self) -> str:
        return self.nome


# Tabela de gastos — registra cada saída de dinheiro.
class Gasto(CamposImutaveisMixin):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="gastos",
    )
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        # Validação em nível de aplicação: rejeita zero e negativos.
        validators=[validar_valor_positivo],
    )
    # PROTECT impede deletar uma categoria que ainda tem gastos.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="gastos",
    )
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ManagerAuditavel()

    class Meta:
        # Mais recente primeiro na listagem padrão.
        ordering: ClassVar = ["-data"]
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        constraints: ClassVar = [
            # Validação em nível de banco: garante valor > 0 no SQL.
            models.CheckConstraint(
                condition=Q(valor__gt=0),
                name="gasto_valor_positivo",
            )
        ]
        indexes: ClassVar = [
            # Cobre filtragens por usuário+data (ordenação padrão e filtros).
            models.Index(
                fields=["usuario", "data"],
                name="idx_gasto_usuario_data",
            ),
            # Cobre filtragens por usuário+categoria+data.
            models.Index(
                fields=["usuario", "categoria", "data"],
                name="idx_gasto_usuario_categoria_data",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.descricao} - R$ {self.valor}"


# Tabela de entradas — registra cada recebimento de dinheiro.
class Entrada(CamposImutaveisMixin):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entradas",
    )
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        # Validação em nível de aplicação: rejeita zero e negativos.
        validators=[validar_valor_positivo],
    )
    # PROTECT impede deletar uma fonte que ainda tem entradas.
    fonte = models.ForeignKey(
        Fonte,
        on_delete=models.PROTECT,
        related_name="entradas",
    )
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ManagerAuditavel()

    class Meta:
        # Mais recente primeiro na listagem padrão.
        ordering: ClassVar = ["-data"]
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        constraints: ClassVar = [
            # Validação em nível de banco: garante valor > 0 no SQL.
            models.CheckConstraint(
                condition=Q(valor__gt=0),
                name="entrada_valor_positivo",
            )
        ]
        indexes: ClassVar = [
            # Cobre filtragens por usuário+data (ordenação padrão e filtros).
            models.Index(
                fields=["usuario", "data"],
                name="idx_entrada_usuario_data",
            ),
            # Cobre filtragens por usuário+fonte+data.
            models.Index(
                fields=["usuario", "fonte", "data"],
                name="idx_entrada_usuario_fonte_data",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.descricao} - R$ {self.valor}"


# Tabela de auditoria — registra toda ação feita sobre os models principais.
class LogAuditoria(models.Model):
    ACOES: ClassVar = [
        ("criado", "Criado"),
        ("atualizado", "Atualizado"),
        ("deletado", "Deletado"),
        ("bulk_deletado", "Bulk Deletado"),
        ("bulk_atualizado", "Bulk Atualizado"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="logs_auditoria",
    )
    acao = models.CharField(max_length=20, choices=ACOES)
    modelo = models.CharField(max_length=50)
    objeto_id = models.PositiveIntegerField()
    detalhes = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)
    # Hash SHA-256 dos campos imutáveis — OWASP prática 130.
    # Permite detectar adulteração direta no banco de dados.
    hash_integridade = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering: ClassVar = ["-criado_em"]
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"

    def __str__(self) -> str:
        return f"{self.acao} {self.modelo} #{self.objeto_id}"

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.hash_integridade:
            self.hash_integridade = self._calcular_hash()
        super().save(*args, **kwargs)

    def _calcular_hash(self) -> str:
        conteudo = json.dumps(
            {
                "usuario_id": self.usuario_id,
                "acao": self.acao,
                "modelo": self.modelo,
                "objeto_id": self.objeto_id,
                "detalhes": self.detalhes,
            },
            sort_keys=True,
            ensure_ascii=True,
        )
        return hashlib.sha256(conteudo.encode()).hexdigest()


# Tabela de acesso — registra toda requisição feita ao sistema.
class LogAcesso(models.Model):
    ORIGENS: ClassVar = [
        ("web", "Web"),
        ("whatsapp", "WhatsApp"),
        ("mobile", "Mobile"),
        ("api", "API"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_acesso",
    )
    metodo = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=255)
    status_code = models.PositiveSmallIntegerField()
    origem = models.CharField(max_length=20, choices=ORIGENS, default="api")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    dispositivo = models.CharField(max_length=20, blank=True, default="")
    duracao_ms = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-criado_em"]
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"

    def __str__(self) -> str:
        usuario = self.usuario or "anonimo"
        return (
            f"{self.metodo} {self.endpoint} [{self.status_code}] — {usuario}"
        )
