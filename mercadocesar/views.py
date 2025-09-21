from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .models import Estoque

@login_required
def home(request):
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