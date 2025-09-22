from django.urls import path
from .views import home, register, estoque_baixo

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('estoque-baixo/', estoque_baixo, name='estoque_baixo'),
]