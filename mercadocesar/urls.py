from django.urls import path
from .views import (pagina_inicial, register, estoque_baixo, buscar_itens, cadastrar_cartao, 
                    listar_cartoes, deletar_cartao, checkout, processar_entrega_domicilio, 
                    processar_entrega_retirada, finalizar_pedido, gerenciar_lojas, ativar_desativar_loja, 
                    visualizar_pedidos)

urlpatterns = [
    path('', pagina_inicial, name='home'),
    path('register/', register, name='register'),
    path('estoque-baixo/', estoque_baixo, name='estoque_baixo'),
    path('busca/', buscar_itens, name= 'busca'),
    path('cadastrar/', cadastrar_cartao, name='cadastrar_cartao'),
    path('cartoes/', listar_cartoes, name='listar_cartoes'),
    path('cartoes/deletar/<int:cartao_id>/', deletar_cartao, name='deletar_cartao'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/domicilio/', processar_entrega_domicilio, name='processar_entrega_domicilio'),
    path('checkout/retirada/', processar_entrega_retirada, name='processar_entrega_retirada'),
    path('checkout/finalizar/', finalizar_pedido, name='finalizar_pedido'),
    path('gerenciar-lojas/', gerenciar_lojas, name='gerenciar_lojas'),
    path('lojas/ativar-desativar/<int:loja_id>/', ativar_desativar_loja, name='ativar_desativar_loja'),
    path('pedidos/', visualizar_pedidos, name='visualizar_pedidos'),
]