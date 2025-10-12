from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Estoque, Produto

@login_required
def pagina_inicial(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def estoque_baixo(request):
    estoques = Estoque.abaixo_estoque_minimo()
    return render(request, 'estoque_baixo.html', {'estoques': estoques})

@login_required
def buscar_itens(request):
    todos_produtos = Produto.objects.all().order_by('categoria', 'id')

    produtos_destaque = []

    categoria_vistas = set()

    for produto in todos_produtos:
        if produto.categoria not in categoria_vistas:
            produtos_destaque.append(produto)
            categoria_vistas.add(produto.categoria)

    contexto = {
        'todos_produtos': todos_produtos,
        'produtos_destaque': produtos_destaque

    }
    
    return render(request, 'buscar_itens.html', contexto)