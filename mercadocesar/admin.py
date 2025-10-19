from django.contrib import admin
from .models import Produto, Estoque, Armazem, CartaoCredito

admin.site.register(Produto)
admin.site.register(Estoque)
admin.site.register(Armazem)

