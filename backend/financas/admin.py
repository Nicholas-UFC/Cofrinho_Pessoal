from django.contrib import admin

from financas.models import Categoria, Entrada, Fonte, Gasto

admin.site.register(Categoria)
admin.site.register(Fonte)
admin.site.register(Gasto)
admin.site.register(Entrada)
