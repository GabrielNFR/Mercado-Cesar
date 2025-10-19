from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Estoque, Produto, CartaoCredito
from .validators import validar_numero_cartao, validar_cvv, validar_validade, identificar_bandeira

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


@login_required
def cadastrar_cartao(request):
    """View para cadastro de cartão de crédito"""
    
    if request.method == 'POST':
        # Pegar dados do formulário
        numero_cartao = request.POST.get('numero_cartao', '').strip()
        nome_titular = request.POST.get('nome_titular', '').strip()
        validade = request.POST.get('validade', '').strip()  # Formato MM/AA
        cvv = request.POST.get('cvv', '').strip()
        apelido = request.POST.get('apelido', '').strip()
        
        # Lista de erros
        erros = []
        
        # Validar campos obrigatórios
        if not numero_cartao:
            erros.append("Número do cartão é obrigatório")
        if not nome_titular:
            erros.append("Nome do titular é obrigatório")
        if not validade:
            erros.append("Validade é obrigatória")
        if not cvv:
            erros.append("CVV é obrigatório")
        
        # Processar validade (formato MM/AA)
        mes_validade = None
        ano_validade = None
        if validade and '/' in validade:
            partes = validade.split('/')
            if len(partes) == 2:
                mes_validade = partes[0].strip()
                ano_validade = partes[1].strip()
            else:
                erros.append("Formato de validade inválido. Use MM/AA")
        else:
            erros.append("Formato de validade inválido. Use MM/AA")
        
        # Se não há erros básicos, validar formato
        if not erros and mes_validade and ano_validade:
            # Validar número do cartão
            valido, msg_erro = validar_numero_cartao(numero_cartao)
            if not valido:
                erros.append(msg_erro)
            
            # Validar CVV
            valido_cvv, msg_erro_cvv = validar_cvv(cvv)
            if not valido_cvv:
                erros.append(msg_erro_cvv)
            
            # Validar validade
            valido_validade, msg_erro_validade = validar_validade(mes_validade, ano_validade)
            if not valido_validade:
                erros.append(msg_erro_validade)
            
            # Validar nome do titular
            if len(nome_titular) < 3:
                erros.append("Nome do titular deve ter pelo menos 3 caracteres")
        
        # Se há erros, exibir mensagem de erro
        if erros:
            messages.error(request, "Dados do cartão inválidos. Verifique as informações e tente novamente.")
            for erro in erros:
                messages.warning(request, erro)
            return render(request, 'cadastrar_cartao.html')
        
        # Se passou nas validações, processar
        # Limpar número do cartão
        import re
        numero_limpo = re.sub(r'[\s-]', '', numero_cartao)
        
        # Pegar últimos 4 dígitos
        ultimos_4 = numero_limpo[-4:]
        
        # Identificar bandeira
        bandeira = identificar_bandeira(numero_limpo)
        
        # Ajustar ano se necessário (2 dígitos -> 4 dígitos)
        ano_int = int(ano_validade)
        if ano_int < 100:
            ano_int += 2000
        
        # Verificar se cartão já existe (mesmo usuário, mesmos últimos 4 dígitos, mesma bandeira)
        cartao_existente = CartaoCredito.objects.filter(
            usuario=request.user,
            ultimos_4_digitos=ultimos_4,
            bandeira=bandeira,
            mes_validade=int(mes_validade),
            ano_validade=ano_int
        ).exists()
        
        if cartao_existente:
            messages.error(request, "Este cartão já está cadastrado na sua conta.")
            contexto = {
                'nome_titular': nome_titular,
                'mes_validade': mes_validade,
                'ano_validade': ano_validade,
                'apelido': apelido,
            }
            return render(request, 'cadastrar_cartao.html', contexto)
        
        # Salvar cartão
        CartaoCredito.objects.create(
            usuario=request.user,
            bandeira=bandeira,
            ultimos_4_digitos=ultimos_4,
            mes_validade=int(mes_validade),
            ano_validade=ano_int,
            apelido=apelido if apelido else None
        )
        
        messages.success(request, "Cartão cadastrado com sucesso.")
        return redirect('listar_cartoes')
    
    return render(request, 'cadastrar_cartao.html')


@login_required
def listar_cartoes(request):
    """View para listar cartões do usuário"""
    cartoes = CartaoCredito.objects.filter(usuario=request.user).order_by('-id')
    
    contexto = {
        'cartoes': cartoes
    }
    
    return render(request, 'listar_cartoes.html', contexto)