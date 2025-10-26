from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from .models import Estoque, Produto, CartaoCredito, Loja, Pedido, Carrinho, ItemCarrinho
from .validators import (validar_numero_cartao, validar_cvv, validar_validade, identificar_bandeira,
                          validar_cep, verificar_area_entrega, calcular_frete, calcular_prazo_entrega)


def obter_carrinho_ativo(usuario):
    """Retorna o carrinho ativo do usuário"""
    return Carrinho.objects.filter(usuario=usuario, ativo=True).first()


class PedidoTemporario:
    """Classe para representar um pedido antes de ser salvo no banco"""
    def __init__(self, dados, carrinho, loja=None):
        self.tipo_entrega = dados['tipo_entrega']
        self.custo_entrega = Decimal(dados['custo_entrega'])
        self.prazo_dias = dados['prazo_dias']
        self._carrinho = carrinho
        self.loja = loja
        
        # Campos específicos de domicílio
        if dados['tipo_entrega'] == 'DOMICILIO':
            self.cep = dados['cep']
            self.endereco = dados['endereco']
            self.numero = dados['numero']
            self.complemento = dados.get('complemento', '')
            self.bairro = dados['bairro']
            self.cidade = dados['cidade']
            self.estado = dados['estado']
    
    @property
    def itens(self):
        return self._carrinho.itens if self._carrinho else []
    
    def calcular_subtotal_produtos(self):
        return self._carrinho.calcular_total() if self._carrinho else Decimal('0')
    
    def calcular_total(self):
        subtotal = self.calcular_subtotal_produtos()
        return Decimal(str(subtotal)) + self.custo_entrega


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
    if request.method == 'POST':
        # Adicionar produto ao carrinho
        produto_id = request.POST.get('produto_id')
        if produto_id:
            try:
                produto = Produto.objects.get(id=produto_id)
                carrinho, created = Carrinho.objects.get_or_create(usuario=request.user, ativo=True)
                item, created = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)
                
                if not created:
                    item.quantidade += 1
                    item.save()
                    messages.success(request, f"{produto.nome} - quantidade atualizada no carrinho")
                else:
                    messages.success(request, f"{produto.nome} adicionado ao carrinho")
            except Produto.DoesNotExist:
                messages.error(request, "Produto não encontrado")
        
        return redirect('busca')
    
    todos_produtos = Produto.objects.all().order_by('categoria', 'id')

    produtos_destaque = []

    categoria_vistas = set()

    for produto in todos_produtos:
        if produto.categoria not in categoria_vistas:
            produtos_destaque.append(produto)
            categoria_vistas.add(produto.categoria)

    # Pegar carrinho atual
    carrinho = obter_carrinho_ativo(request.user)
    total_itens = sum(item.quantidade for item in carrinho.itens.all()) if carrinho else 0

    contexto = {
        'todos_produtos': todos_produtos,
        'produtos_destaque': produtos_destaque,
        'carrinho': carrinho,
        'total_itens': total_itens
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


@login_required
def deletar_cartao(request, cartao_id):
    """View para deletar um cartão de crédito"""
    if request.method == 'POST':
        try:
            cartao = CartaoCredito.objects.get(id=cartao_id, usuario=request.user)
            cartao.delete()
            messages.success(request, "Cartão deletado com sucesso.")
            return redirect('listar_cartoes')
        except CartaoCredito.DoesNotExist:
            messages.error(request, "Cartão não encontrado.")
            return redirect('listar_cartoes')
    else:
        return redirect('listar_cartoes')


@login_required
def checkout(request):
    """View para escolher tipo de entrega"""
    # Verificar se há carrinho ativo com itens
    carrinho = obter_carrinho_ativo(request.user)
    
    if not carrinho or not carrinho.itens.exists():
        messages.warning(request, "Seu carrinho está vazio. Adicione produtos antes de finalizar.")
        return redirect('busca')
    
    lojas = Loja.objects.filter(ativa=True)
    return render(request, 'checkout.html', {'lojas': lojas, 'carrinho': carrinho})


@login_required
def processar_entrega_domicilio(request):
    """View para processar entrega em domicílio"""
    if request.method != 'POST':
        return redirect('checkout')
    
    cep = request.POST.get('cep', '').strip()
    endereco = request.POST.get('endereco', '').strip()
    numero = request.POST.get('numero', '').strip()
    complemento = request.POST.get('complemento', '').strip()
    bairro = request.POST.get('bairro', '').strip()
    cidade = request.POST.get('cidade', '').strip()
    estado = request.POST.get('estado', '').strip()
    
    erros = []
    
    if not cep:
        erros.append("CEP é obrigatório")
    if not endereco:
        erros.append("Endereço é obrigatório")
    if not numero:
        erros.append("Número é obrigatório")
    if not bairro:
        erros.append("Bairro é obrigatório")
    if not cidade:
        erros.append("Cidade é obrigatória")
    if not estado:
        erros.append("Estado é obrigatório")
    
    if cep:
        valido, mensagem = validar_cep(cep)
        if not valido:
            erros.append(mensagem)
        else:
            disponivel, mensagem_area = verificar_area_entrega(cep)
            if not disponivel:
                messages.error(request, mensagem_area)
                lojas = Loja.objects.filter(ativa=True)
                return render(request, 'checkout.html', {'lojas': lojas, 'cep': cep})
    
    if erros:
        for erro in erros:
            messages.error(request, erro)
        lojas = Loja.objects.filter(ativa=True)
        return render(request, 'checkout.html', {'lojas': lojas})
    
    custo_entrega = calcular_frete(cep)
    prazo_dias = calcular_prazo_entrega(cep)
    
    # Armazenar dados na sessão
    request.session['pedido_temp'] = {
        'tipo_entrega': 'DOMICILIO',
        'cep': cep,
        'endereco': endereco,
        'numero': numero,
        'complemento': complemento,
        'bairro': bairro,
        'cidade': cidade,
        'estado': estado,
        'custo_entrega': str(custo_entrega),
        'prazo_dias': prazo_dias,
    }
    
    # Buscar carrinho para mostrar na revisão
    carrinho = obter_carrinho_ativo(request.user)
    
    # Buscar cartões do usuário
    cartoes = CartaoCredito.objects.filter(usuario=request.user)
    
    # Criar objeto temporário para passar para o template
    pedido_temp = PedidoTemporario(request.session['pedido_temp'], carrinho)
    return render(request, 'confirmacao_pedido.html', {
        'pedido': pedido_temp, 
        'em_revisao': True,
        'cartoes': cartoes
    })


@login_required
def processar_entrega_retirada(request):
    """View para processar retirada na loja"""
    if request.method != 'POST':
        return redirect('checkout')
    
    loja_id = request.POST.get('loja_id')
    
    if not loja_id:
        messages.error(request, "Selecione uma loja para retirada")
        return redirect('checkout')
    
    try:
        loja = Loja.objects.get(id=loja_id, ativa=True)
    except Loja.DoesNotExist:
        messages.error(request, "Loja não encontrada")
        return redirect('checkout')
    
    # Armazenar dados na sessão
    request.session['pedido_temp'] = {
        'tipo_entrega': 'RETIRADA',
        'loja_id': loja.id,
        'custo_entrega': '0',
        'prazo_dias': loja.prazo_retirada_dias,
    }
    
    # Buscar carrinho para mostrar na revisão
    carrinho = obter_carrinho_ativo(request.user)
    
    # Buscar cartões do usuário
    cartoes = CartaoCredito.objects.filter(usuario=request.user)
    
    # Criar objeto temporário para passar para o template
    pedido_temp = PedidoTemporario(request.session['pedido_temp'], carrinho, loja)
    return render(request, 'confirmacao_pedido.html', {
        'pedido': pedido_temp, 
        'loja': loja, 
        'em_revisao': True,
        'cartoes': cartoes
    })


@login_required
def finalizar_pedido(request):
    """Finaliza o pedido após revisão"""
    if request.method != 'POST':
        return redirect('checkout')
    
    pedido_dados = request.session.get('pedido_temp')
    
    if not pedido_dados:
        messages.error(request, "Nenhum pedido para finalizar")
        return redirect('checkout')
    
    # Validar cartão selecionado
    cartao_id = request.POST.get('cartao_id')
    
    if not cartao_id:
        messages.error(request, "Selecione um cartão de crédito para pagamento")
        return redirect('checkout')
    
    try:
        cartao = CartaoCredito.objects.get(id=cartao_id, usuario=request.user)
    except CartaoCredito.DoesNotExist:
        messages.error(request, "Cartão inválido ou não pertence a você")
        return redirect('checkout')
    
    # Buscar carrinho ativo
    carrinho = obter_carrinho_ativo(request.user)
    
    if not carrinho or not carrinho.itens.exists():
        messages.error(request, "Seu carrinho está vazio")
        return redirect('busca')
    
    from .models import ItemPedido
    
    # Criar o pedido real
    if pedido_dados['tipo_entrega'] == 'DOMICILIO':
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_entrega='DOMICILIO',
            cep=pedido_dados['cep'],
            endereco=pedido_dados['endereco'],
            numero=pedido_dados['numero'],
            complemento=pedido_dados.get('complemento', ''),
            bairro=pedido_dados['bairro'],
            cidade=pedido_dados['cidade'],
            estado=pedido_dados['estado'],
            custo_entrega=Decimal(pedido_dados['custo_entrega']),
            prazo_dias=pedido_dados['prazo_dias'],
            cartao=cartao
        )
        loja = None
    else:  
        loja = Loja.objects.get(id=pedido_dados['loja_id'])
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_entrega='RETIRADA',
            loja=loja,
            custo_entrega=Decimal(pedido_dados['custo_entrega']),
            prazo_dias=pedido_dados['prazo_dias'],
            cartao=cartao
        )
    
    # Copiar itens do carrinho para o pedido
    for item_carrinho in carrinho.itens.all():
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item_carrinho.produto,
            quantidade=item_carrinho.quantidade,
            preco_unitario=item_carrinho.produto.preco
        )
    
    # Desativar o carrinho
    carrinho.ativo = False
    carrinho.save()
    
    # Limpar sessão
    del request.session['pedido_temp']
    
    messages.success(request, f"Pedido #{pedido.id} confirmado com sucesso!")
    
    if loja:
        return render(request, 'confirmacao_pedido.html', {'pedido': pedido, 'loja': loja})
    else:
        return render(request, 'confirmacao_pedido.html', {'pedido': pedido})


@user_passes_test(lambda u: u.is_superuser)
def gerenciar_lojas(request):
    """View para superusuário gerenciar lojas"""
    if request.method == 'POST':
        # Criar nova loja
        nome = request.POST.get('nome')
        endereco = request.POST.get('endereco')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        prazo_retirada_dias = request.POST.get('prazo_retirada_dias', 1)
        
        if nome and endereco and numero and bairro and cidade and estado and cep:
            Loja.objects.create(
                nome=nome,
                endereco=endereco,
                numero=numero,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                cep=cep,
                prazo_retirada_dias=prazo_retirada_dias,
                ativa=True
            )
            messages.success(request, f"Loja '{nome}' cadastrada com sucesso!")
        else:
            messages.error(request, "Preencha todos os campos obrigatórios")
        
        return redirect('gerenciar_lojas')
    
    lojas = Loja.objects.all().order_by('-ativa', 'nome')
    return render(request, 'gerenciar_lojas.html', {'lojas': lojas})


@user_passes_test(lambda u: u.is_superuser)
def ativar_desativar_loja(request, loja_id):
    """Toggle status ativo/inativo de uma loja"""
    try:
        loja = Loja.objects.get(id=loja_id)
        loja.ativa = not loja.ativa
        loja.save()
        status = "ativada" if loja.ativa else "desativada"
        messages.success(request, f"Loja '{loja.nome}' {status} com sucesso!")
    except Loja.DoesNotExist:
        messages.error(request, "Loja não encontrada")
    
    return redirect('gerenciar_lojas')


@user_passes_test(lambda u: u.is_superuser)
def visualizar_pedidos(request):
    """View para superusuário visualizar todos os pedidos"""
    from .models import ItemPedido
    
    # Filtros
    tipo_entrega = request.GET.get('tipo_entrega', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    pedidos = Pedido.objects.all().select_related('usuario', 'loja').prefetch_related('itens__produto')
    
    if tipo_entrega:
        pedidos = pedidos.filter(tipo_entrega=tipo_entrega)
    
    if data_inicio:
        pedidos = pedidos.filter(data_criacao__date__gte=data_inicio)
    
    if data_fim:
        pedidos = pedidos.filter(data_criacao__date__lte=data_fim)
    
    pedidos = pedidos.order_by('-data_criacao')
    
    context = {
        'pedidos': pedidos,
        'tipo_entrega_filtro': tipo_entrega,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    
    return render(request, 'visualizar_pedidos.html', context)
