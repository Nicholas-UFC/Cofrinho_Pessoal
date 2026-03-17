from typing import ClassVar

from django.db import models
from django.db.models import Q

from financas.validators import validar_valor_positivo

# Campos que nunca devem ser alterados após a criação do registro.
# O método save() usa essa lista para excluí-los de qualquer UPDATE.
_CAMPOS_IMUTAVEIS = {"id", "criado_em"}


# Tabela de categorias de gastos (ex: Alimentação, Transporte).
# Usada como chave estrangeira em Gasto.
class Categoria(models.Model):
    # Nome único — não permite duas categorias com o mesmo nome.
    nome = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["nome"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self) -> str:
        return self.nome

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


# Tabela de fontes de renda (ex: Salário, Freelance).
# Usada como chave estrangeira em Entrada.
class Fonte(models.Model):
    # Nome único — não permite duas fontes com o mesmo nome.
    nome = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["nome"]
        verbose_name = "Fonte"
        verbose_name_plural = "Fontes"

    def __str__(self) -> str:
        return self.nome

    def save(self, *args: object, **kwargs: object) -> None:
        # Mesma proteção de campos imutáveis aplicada em Categoria.
        if self.pk and "update_fields" not in kwargs:
            updatable = [
                f.name
                for f in self._meta.local_fields
                if f.name not in _CAMPOS_IMUTAVEIS
            ]
            kwargs["update_fields"] = updatable
        super().save(*args, **kwargs)


# Tabela de gastos — registra cada saída de dinheiro.
class Gasto(models.Model):
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

    def save(self, *args: object, **kwargs: object) -> None:
        # Mesma proteção de campos imutáveis aplicada em Categoria.
        if self.pk and "update_fields" not in kwargs:
            updatable = [
                f.name
                for f in self._meta.local_fields
                if f.name not in _CAMPOS_IMUTAVEIS
            ]
            kwargs["update_fields"] = updatable
        super().save(*args, **kwargs)


# Tabela de entradas — registra cada recebimento de dinheiro.
class Entrada(models.Model):
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

    def save(self, *args: object, **kwargs: object) -> None:
        # Mesma proteção de campos imutáveis aplicada em Categoria.
        if self.pk and "update_fields" not in kwargs:
            updatable = [
                f.name
                for f in self._meta.local_fields
                if f.name not in _CAMPOS_IMUTAVEIS
            ]
            kwargs["update_fields"] = updatable
        super().save(*args, **kwargs)
