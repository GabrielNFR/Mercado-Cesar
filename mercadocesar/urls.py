from django.urls import path
from .views import pagina_inicial, register, estoque_baixo, buscar_itens

urlpatterns = [
    path('', pagina_inicial, name='home'),
    path('register/', register, name='register'),
    path('estoque-baixo/', estoque_baixo, name='estoque_baixo'),
    path('busca/', buscar_itens, name= 'busca'),
]