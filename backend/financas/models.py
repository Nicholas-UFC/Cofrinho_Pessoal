from typing import ClassVar

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from financas.validators import validar_valor_positivo

# Campos que nunca devem ser alterados após a criação do registro.
_CAMPOS_IMUTAVEIS = {"id", "criado_em"}


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

    def __str__(self) -> str:
        return f"{self.descricao} - R$ {self.valor}"
