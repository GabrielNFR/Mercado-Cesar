from django.contrib import admin
from .models import Produto, Estoque, Armazem, ItemCarrinho, Pedido, ItemPedido

admin.site.register(Produto)
admin.site.register(Estoque)
admin.site.register(Armazem)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('preco_unitario',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_entrega', 'data_criacao', 'calcular_total')
    list_filter = ('tipo_entrega', 'data_criacao')
    search_fields = ('usuario__username', 'id')
    inlines = [ItemPedidoInline]
    readonly_fields = ('data_criacao',)

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'preco_unitario')


