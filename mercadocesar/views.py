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
        self.id = None  # Pedido ainda não foi criado
        self.cartao = None  # Cartão ainda não foi selecionado
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
    """Landing page com produtos em destaque e informações"""
    from django.db.models import Sum, Count
    
    # Buscar os 3 produtos mais pedidos (baseado na quantidade total vendida)
    produtos_mais_pedidos = Produto.objects.annotate(
        total_vendido=Sum('itempedido__quantidade')
    ).filter(
        total_vendido__isnull=False  # Apenas produtos que já foram pedidos
    ).order_by('-total_vendido')[:3]
    
    # Se não houver produtos pedidos ainda, mostra os primeiros 3 produtos disponíveis
    if not produtos_mais_pedidos.exists():
        produtos_destaque = Produto.objects.all()[:3]
    else:
        produtos_destaque = produtos_mais_pedidos
    
    # Buscar lojas ativas
    lojas = Loja.objects.filter(ativa=True)[:3]
    
    contexto = {
        'produtos_destaque': produtos_destaque,
        'lojas': lojas,
    }
    
    return render(request, 'home.html', contexto)


def politica_privacidade(request):
    """Página de Política de Privacidade"""
    return render(request, 'politica_privacidade.html')


def termos_uso(request):
    """Página de Termos de Uso"""
    return render(request, 'termos_uso.html')

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
    # Pegar estoques com quantidade < 30
    estoques = list(Estoque.abaixo_estoque_minimo())
    
    # Adicionar produtos que não têm nenhum registro de estoque (estoque total = 0)
    from django.db.models import Sum
    produtos_sem_estoque = Produto.objects.annotate(
        total_estoque=Sum('estoque__quantidade')
    ).filter(total_estoque__isnull=True)
    
    # Criar objetos fictícios de Estoque para produtos sem estoque
    class EstoqueFicticio:
        def __init__(self, produto):
            self.produto = produto
            self.quantidade = 0
            self.armazem = type('obj', (object,), {'nome': 'Nenhum'})()
    
    for produto in produtos_sem_estoque:
        estoques.append(EstoqueFicticio(produto))
    
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
    
    # Verificar se é requisição AJAX para repetir pedido
    if request.method == 'POST':
        import json
        from django.http import JsonResponse
        
        try:
            data = json.loads(request.body)
            
            if data.get('acao') == 'repetir_pedido':
                pedido_id = data.get('pedido_id')
                
                # Buscar pedido original (apenas do usuário logado por segurança)
                try:
                    from .models import ItemPedido
                    pedido_original = Pedido.objects.get(id=pedido_id, usuario=request.user)
                except Pedido.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Pedido não encontrado ou não pertence a você'})
                
                # Desativar carrinho atual (se existir)
                Carrinho.objects.filter(usuario=request.user, ativo=True).update(ativo=False)
                
                # Criar novo carrinho
                novo_carrinho = Carrinho.objects.create(usuario=request.user, ativo=True)
                
                # Recriar itens do carrinho baseado no pedido
                itens_pedido = ItemPedido.objects.filter(pedido=pedido_original).select_related('produto')
                
                for item in itens_pedido:
                    ItemCarrinho.objects.create(
                        carrinho=novo_carrinho,
                        produto=item.produto,
                        quantidade=item.quantidade
                    )
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Pedido #{pedido_id} adicionado ao carrinho com {itens_pedido.count()} itens!'
                })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request normal - exibir checkout
    carrinho = obter_carrinho_ativo(request.user)
    
    # Sempre renderizar a página checkout para permitir que o JavaScript
    # de compra rápida execute. O template vai mostrar mensagem apropriada
    # se o carrinho estiver vazio após o JavaScript executar.
    lojas = Loja.objects.filter(ativa=True)
    
    # Se carrinho vazio, deixar o template decidir (pode ser compra rápida via JS)
    if not carrinho or not carrinho.itens.exists():
        return render(request, 'checkout.html', {'lojas': lojas, 'carrinho': None})
    return render(request, 'checkout.html', {'lojas': lojas, 'carrinho': carrinho})


@login_required
def atualizar_quantidade_carrinho(request, item_id):
    """Atualiza a quantidade de um item no carrinho"""
    if request.method != 'POST':
        return redirect('checkout')
    
    try:
        item = ItemCarrinho.objects.get(id=item_id, carrinho__usuario=request.user, carrinho__ativo=True)
        acao = request.POST.get('acao') 
        
        estoque_total = item.produto.estoque_total()
        
        if acao == 'aumentar':
            if item.quantidade >= estoque_total:
                messages.warning(request, f'Estoque insuficiente. Apenas {estoque_total} unidade(s) disponível(is).')
            else:
                item.quantidade += 1
                item.save()
        elif acao == 'diminuir':
            if item.quantidade <= 1:
                # Quantidade chegou a 0, remover item
                produto_nome = item.produto.nome
                item.delete()
                messages.success(request, f'"{produto_nome}" removido do carrinho.')
            else:
                item.quantidade -= 1
                item.save()
    
    except ItemCarrinho.DoesNotExist:
        messages.error(request, 'Item não encontrado no carrinho.')
    
    return redirect('checkout')


@login_required
def remover_item_carrinho(request, item_id):
    """Remove quantidade específica de um item do carrinho"""
    if request.method != 'POST':
        return redirect('checkout')
    
    try:
        item = ItemCarrinho.objects.get(id=item_id, carrinho__usuario=request.user, carrinho__ativo=True)
        produto_nome = item.produto.nome
        quantidade_atual = item.quantidade
        
        # Obter quantidade a remover (padrão é tudo)
        quantidade_remover = int(request.POST.get('quantidade_remover', quantidade_atual))
        
        # Validar quantidade
        if quantidade_remover <= 0:
            messages.error(request, 'Quantidade inválida.')
            return redirect('checkout')
        
        if quantidade_remover >= quantidade_atual:
            # Remover item completamente
            item.delete()
            messages.success(request, f'"{produto_nome}" removido completamente do carrinho.')
        else:
            # Reduzir quantidade
            item.quantidade -= quantidade_remover
            item.save()
            messages.success(request, f'{quantidade_remover} unidade(s) de "{produto_nome}" removida(s). Restam {item.quantidade} no carrinho.')
    
    except ItemCarrinho.DoesNotExist:
        messages.error(request, 'Item não encontrado no carrinho.')
    except ValueError:
        messages.error(request, 'Quantidade inválida.')
    
    return redirect('checkout')


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
    
    # Validar estoque disponível antes de criar o pedido
    erros_estoque = []
    for item in carrinho.itens.all():
        estoque_disponivel = item.produto.estoque_total()
        if estoque_disponivel < item.quantidade:
            erros_estoque.append(
                f"{item.produto.nome}: estoque insuficiente (disponível: {estoque_disponivel}, solicitado: {item.quantidade})"
            )
    
    if erros_estoque:
        for erro in erros_estoque:
            messages.error(request, erro)
        return redirect('checkout')
    
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
    
    # Reduzir estoque dos produtos
    for item_carrinho in carrinho.itens.all():
        quantidade_restante = item_carrinho.quantidade
        
        # Buscar estoques do produto ordenados por quantidade decrescente
        # (prioriza armazéns com mais estoque)
        estoques = Estoque.objects.filter(
            produto=item_carrinho.produto, 
            quantidade__gt=0
        ).order_by('-quantidade')
        
        # Reduzir estoque de um ou mais armazéns conforme necessário
        for estoque in estoques:
            if quantidade_restante <= 0:
                break
            
            if estoque.quantidade >= quantidade_restante:
                # Este armazém tem estoque suficiente
                estoque.quantidade -= quantidade_restante
                quantidade_restante = 0
            else:
                # Este armazém não tem estoque suficiente, usar tudo
                quantidade_restante -= estoque.quantidade
                estoque.quantidade = 0
            
            estoque.save()
    
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

@user_passes_test(lambda u: u.is_staff)
def gerenciar_produtos(request):
    """Gerencia produtos com todas as operações CRUD em uma única view"""
    from django.shortcuts import get_object_or_404
    
    action = request.GET.get('action', 'list')
    produto_id = request.GET.get('id')
    
    if action == 'delete' and produto_id:
        produto = get_object_or_404(Produto, id=produto_id)
        if request.method == 'POST':
            nome = produto.nome
            produto.delete()
            messages.success(request, f'Produto "{nome}" removido com sucesso!')
            return redirect('gerenciar_produtos')
        return render(request, 'produtos.html', {'action': 'delete', 'produto': produto})
    
    if action == 'edit' and produto_id:
        produto = get_object_or_404(Produto, id=produto_id)
        if request.method == 'POST':
            try:
                preco_custo = Decimal(request.POST.get('preco_custo'))
                preco = Decimal(request.POST.get('preco'))
                
                if preco_custo < 0 or preco < 0:
                    messages.error(request, 'Preços não podem ser negativos.')
                    return render(request, 'produtos.html', {'action': 'edit', 'produto': produto})
                
                produto.codigo = request.POST.get('codigo')
                produto.nome = request.POST.get('nome')
                produto.descricao = request.POST.get('descricao')
                produto.categoria = request.POST.get('categoria')
                produto.preco_custo = preco_custo
                produto.preco = preco
                produto.unidade_medida = request.POST.get('unidade_medida')
                produto.save()
                messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
                return redirect('gerenciar_produtos')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar produto: {str(e)}')
        return render(request, 'produtos.html', {'action': 'edit', 'produto': produto})
    
    if action == 'add':
        if request.method == 'POST':
            try:
                preco_custo = Decimal(request.POST.get('preco_custo'))
                preco = Decimal(request.POST.get('preco'))
                
                if preco_custo < 0 or preco < 0:
                    messages.error(request, 'Preços não podem ser negativos.')
                    return render(request, 'produtos.html', {'action': 'add'})
                
                produto = Produto.objects.create(
                    codigo=request.POST.get('codigo'),
                    nome=request.POST.get('nome'),
                    descricao=request.POST.get('descricao'),
                    categoria=request.POST.get('categoria'),
                    preco_custo=preco_custo,
                    preco=preco,
                    unidade_medida=request.POST.get('unidade_medida'),
                )
                messages.success(request, f'Produto "{produto.nome}" cadastrado com sucesso!')
                return redirect('gerenciar_produtos')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar produto: {str(e)}')
        return render(request, 'produtos.html', {'action': 'add'})
    
    produtos = Produto.objects.all().order_by('codigo')
    busca = request.GET.get('busca', '')
    categoria = request.GET.get('categoria', '')
    
    if busca:
        produtos = produtos.filter(
            Q(codigo__icontains=busca) | 
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    if categoria:
        produtos = produtos.filter(categoria__icontains=categoria)
    
    categorias_disponiveis = Produto.objects.values_list('categoria', flat=True).distinct()
    
    context = {
        'action': 'list',
        'produtos': produtos,
        'busca': busca,
        'categoria': categoria,
        'categorias': categorias_disponiveis,
    }
    
    return render(request, 'produtos.html', context)


@user_passes_test(lambda u: u.is_staff)
def adicionar_produto(request):
    """Redireciona para a view unificada"""
    return redirect('gerenciar_produtos' + '?action=add')


@user_passes_test(lambda u: u.is_staff)
def editar_produto(request, produto_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_produtos?action=edit&id={produto_id}')


@user_passes_test(lambda u: u.is_staff)
def deletar_produto(request, produto_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_produtos?action=delete&id={produto_id}')


@user_passes_test(lambda u: u.is_staff)
def gerenciar_armazens(request):
    """Gerencia armazéns com todas as operações CRUD em uma única view"""
    from django.shortcuts import get_object_or_404
    from .models import Armazem
    
    action = request.GET.get('action', 'list')
    armazem_id = request.GET.get('id')
    
    if action == 'delete' and armazem_id:
        armazem = get_object_or_404(Armazem, id=armazem_id)
        if request.method == 'POST':
            nome = armazem.nome
            armazem.delete()
            messages.success(request, f'Armazém "{nome}" removido com sucesso!')
            return redirect('gerenciar_armazens')
        return render(request, 'armazens.html', {'action': 'delete', 'armazem': armazem})
    
    if action == 'edit' and armazem_id:
        armazem = get_object_or_404(Armazem, id=armazem_id)
        if request.method == 'POST':
            try:
                armazem.nome = request.POST.get('nome')
                armazem.endereco = request.POST.get('endereco', '')
                armazem.save()
                messages.success(request, f'Armazém "{armazem.nome}" atualizado com sucesso!')
                return redirect('gerenciar_armazens')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar armazém: {str(e)}')
        return render(request, 'armazens.html', {'action': 'edit', 'armazem': armazem})
    
    if action == 'add':
        if request.method == 'POST':
            try:
                armazem = Armazem.objects.create(
                    nome=request.POST.get('nome'),
                    endereco=request.POST.get('endereco', ''),
                )
                messages.success(request, f'Armazém "{armazem.nome}" cadastrado com sucesso!')
                return redirect('gerenciar_armazens')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar armazém: {str(e)}')
        return render(request, 'armazens.html', {'action': 'add'})
    
    armazens = Armazem.objects.all().order_by('nome')
    context = {'action': 'list', 'armazens': armazens}
    return render(request, 'armazens.html', context)


@user_passes_test(lambda u: u.is_staff)
def adicionar_armazem(request):
    """Redireciona para a view unificada"""
    return redirect('gerenciar_armazens' + '?action=add')


@user_passes_test(lambda u: u.is_staff)
def editar_armazem(request, armazem_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_armazens?action=edit&id={armazem_id}')


@user_passes_test(lambda u: u.is_staff)
def deletar_armazem(request, armazem_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_armazens?action=delete&id={armazem_id}')


@user_passes_test(lambda u: u.is_staff)
def gerenciar_estoque(request):
    """Gerencia estoque com todas as operações CRUD em uma única view"""
    from django.shortcuts import get_object_or_404
    from .models import Armazem
    
    action = request.GET.get('action', 'list')
    estoque_id = request.GET.get('id')
    
    if action == 'delete' and estoque_id:
        estoque = get_object_or_404(Estoque, id=estoque_id)
        if request.method == 'POST':
            produto_nome = estoque.produto.nome
            armazem_nome = estoque.armazem.nome
            estoque.delete()
            messages.success(request, f'Estoque de "{produto_nome}" em "{armazem_nome}" removido com sucesso!')
            return redirect('gerenciar_estoque')
        return render(request, 'estoque.html', {'action': 'delete', 'estoque': estoque})
    
    if action == 'edit' and estoque_id:
        estoque = get_object_or_404(Estoque, id=estoque_id)
        if request.method == 'POST':
            try:
                nova_quantidade = int(request.POST.get('quantidade'))
                novo_armazem_id = int(request.POST.get('armazem'))
                
                # Se mudou o armazém
                if novo_armazem_id != estoque.armazem.id:
                    novo_armazem = Armazem.objects.get(id=novo_armazem_id)
                    produto = estoque.produto
                    armazem_antigo = estoque.armazem
                    
                    # Verifica se já existe estoque do mesmo produto no novo armazém
                    estoque_existente = Estoque.objects.filter(
                        produto=produto,
                        armazem=novo_armazem
                    ).first()
                    
                    if estoque_existente:
                        # Soma as quantidades
                        estoque_existente.quantidade += nova_quantidade
                        estoque_existente.save()
                        # Remove o estoque antigo
                        estoque.delete()
                        messages.success(
                            request, 
                            f'Estoque de "{produto.nome}" transferido de "{armazem_antigo.nome}" para "{novo_armazem.nome}". '
                            f'Quantidade somada: {estoque_existente.quantidade} unidades no total.'
                        )
                    else:
                        # Move para o novo armazém
                        estoque.armazem = novo_armazem
                        estoque.quantidade = nova_quantidade
                        estoque.save()
                        messages.success(
                            request, 
                            f'Estoque de "{produto.nome}" transferido de "{armazem_antigo.nome}" para "{novo_armazem.nome}" '
                            f'com {nova_quantidade} unidades!'
                        )
                else:
                    # Apenas atualiza a quantidade
                    estoque.quantidade = nova_quantidade
                    estoque.save()
                    messages.success(request, f'Estoque de "{estoque.produto.nome}" em "{estoque.armazem.nome}" atualizado para {estoque.quantidade} unidades!')
                
                return redirect('gerenciar_estoque')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar estoque: {str(e)}')
        
        armazens = Armazem.objects.all().order_by('nome')
        return render(request, 'estoque.html', {'action': 'edit', 'estoque': estoque, 'armazens': armazens})
    
    if action == 'add':
        if request.method == 'POST':
            try:
                produto_id = request.POST.get('produto')
                armazem_id = request.POST.get('armazem')
                quantidade = int(request.POST.get('quantidade'))
                
                produto = Produto.objects.get(id=produto_id)
                armazem = Armazem.objects.get(id=armazem_id)
                
                # Verifica se já existe estoque para esse produto nesse armazém
                estoque, created = Estoque.objects.get_or_create(
                    produto=produto,
                    armazem=armazem,
                    defaults={'quantidade': quantidade}
                )
                
                if not created:
                    # Se já existe, atualiza a quantidade
                    estoque.quantidade = quantidade
                    estoque.save()
                    messages.success(request, f'Estoque de "{produto.nome}" em "{armazem.nome}" atualizado para {quantidade} unidades!')
                else:
                    messages.success(request, f'Estoque de "{produto.nome}" em "{armazem.nome}" cadastrado com {quantidade} unidades!')
                
                return redirect('gerenciar_estoque')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar estoque: {str(e)}')
        
        produtos = Produto.objects.all().order_by('nome')
        armazens = Armazem.objects.all().order_by('nome')
        return render(request, 'estoque.html', {'action': 'add', 'produtos': produtos, 'armazens': armazens})
    
    estoques = Estoque.objects.all().select_related('produto', 'armazem').order_by('produto__codigo', 'armazem__nome')
    busca_produto = request.GET.get('busca_produto', '')
    armazem_id = request.GET.get('armazem', '')
    apenas_baixo = request.GET.get('apenas_baixo', '')
    
    if busca_produto:
        estoques = estoques.filter(
            Q(produto__codigo__icontains=busca_produto) |
            Q(produto__nome__icontains=busca_produto)
        )
    
    if armazem_id:
        estoques = estoques.filter(armazem_id=armazem_id)
    
    if apenas_baixo:
        estoques = estoques.filter(quantidade__lt=30)
    
    armazens = Armazem.objects.all()
    
    context = {
        'action': 'list',
        'estoques': estoques,
        'armazens': armazens,
        'busca_produto': busca_produto,
        'armazem_selecionado': armazem_id,
        'apenas_baixo': apenas_baixo,
    }
    
    return render(request, 'estoque.html', context)


@user_passes_test(lambda u: u.is_staff)
def adicionar_estoque(request):
    """Redireciona para a view unificada"""
    return redirect('gerenciar_estoque' + '?action=add')


@user_passes_test(lambda u: u.is_staff)
def editar_estoque(request, estoque_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_estoque?action=edit&id={estoque_id}')


@user_passes_test(lambda u: u.is_staff)
def deletar_estoque(request, estoque_id):
    """Redireciona para a view unificada"""
    return redirect(f'gerenciar_estoque?action=delete&id={estoque_id}')

@login_required
def pedidos_recentes(request):
    """View para visualizar pedidos recém-feitos com filtros"""
    from .models import Pedido

    # Obter parâmetros de filtro
    usuario = request.GET.get('usuario', '')
    data_fim = request.GET.get('data_fim', '')
    tipo_entrega = request.GET.get('tipo_entrega', '')
    valor = request.GET.get('custo_entrega', '')
    
    # Query base com otimização
    pedidos = Pedido.objects.filter(usuario=request.user) \
        .select_related('usuario', 'loja') \
        .prefetch_related('itens__produto')
    # Aplicar filtros
    if usuario:
        pedidos = pedidos.filter(usuario__username__icontains=usuario)
    
    if data_fim:
        pedidos = pedidos.filter(data_criacao__date__lte=data_fim)
    
    if tipo_entrega:
        pedidos = pedidos.filter(tipo_entrega=tipo_entrega)
    
    if valor:
        pedidos = pedidos.filter(custo_entrega=valor)

    # Ordenar por data de criação (mais recentes primeiro)
    pedidos = pedidos.order_by('-data_criacao')

    context = {
        'usuario': usuario,
        'pedidos': pedidos,
        'tipo_entrega': tipo_entrega,
        'valor': valor,
        'data_fim': data_fim
    }

    return render(request, 'pedidos_recentes.html', context)