from django.urls import path
from .views import pagina_inicial, register, estoque_baixo, buscar_itens, cadastrar_cartao, listar_cartoes, deletar_cartao

urlpatterns = [
    path('', pagina_inicial, name='home'),
    path('register/', register, name='register'),
    path('estoque-baixo/', estoque_baixo, name='estoque_baixo'),
    path('busca/', buscar_itens, name= 'busca'),
    path('cadastrar/', cadastrar_cartao, name='cadastrar_cartao'),
    path('cartoes/', listar_cartoes, name='listar_cartoes'),
    path('cartoes/deletar/<int:cartao_id>/', deletar_cartao, name='deletar_cartao'),
]