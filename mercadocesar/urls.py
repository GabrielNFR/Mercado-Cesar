from django.urls import path
from .views import pagina_inicial, register, estoque_baixo, buscar_itens, cadastrar_cartao, listar_cartoes

urlpatterns = [
    path('', pagina_inicial, name='home'),
    path('register/', register, name='register'),
    path('estoque-baixo/', estoque_baixo, name='estoque_baixo'),
    path('busca/', buscar_itens, name= 'busca'),
    path('cartoes/', listar_cartoes, name='listar_cartoes'),
    path('cartoes/cadastrar/', cadastrar_cartao, name='cadastrar_cartao'),
]