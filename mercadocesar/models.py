from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator
from django.conf import settings


class Produto(models.Model):
	nome = models.CharField(max_length=30, unique=True)
	codigo = models.CharField(max_length=30, unique=True)
	descricao = models.CharField(max_length=200, default="", unique=True)
	categoria = models.CharField(max_length=50)
	preco_custo = models.DecimalField(
		max_digits=10, 
		decimal_places=2,
		validators=[MinValueValidator(0)] 
	)
	preco = models.DecimalField(
		max_digits=10, 
		decimal_places=2,
		validators=[MinValueValidator(0)] 
	)
	unidade_medida = models.CharField(max_length=20)
	imagem = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Imagem do Produto")

	class Meta:
		constraints = [
			CheckConstraint(check=~Q(codigo=""), name='codigo_nao_vazio'),
   			CheckConstraint(check=~Q(descricao=""), name='descricao_nao_vazia'),
			CheckConstraint(check=~Q(categoria=""), name='categoria_nao_vazia'),
			CheckConstraint(check=~Q(unidade_medida=""), name='unidade_medida_nao_vazia'),
		]

	def __str__(self):
		return f"{self.codigo} - {self.descricao} - {self.categoria}"
	
	def estoque_total(self):
		from django.db.models import Sum
		total = self.estoque_set.aggregate(Sum('quantidade'))['quantidade__sum']
		return total if total is not None else 0


class Armazem(models.Model):
	nome = models.CharField(max_length=100)
	endereco = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return self.nome

	class Meta:
		verbose_name_plural = "Armazéns"


class Estoque(models.Model):
	produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
	armazem = models.ForeignKey(Armazem, on_delete=models.CASCADE)
	quantidade = models.PositiveIntegerField()

	class Meta:
		unique_together = ('produto', 'armazem')

	def __str__(self):
		return f"{self.produto} em {self.armazem}: {self.quantidade}"

	@staticmethod
	def abaixo_estoque_minimo(minimo=30):
		return Estoque.objects.filter(quantidade__lt=minimo)

class CartaoCredito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='cartoes'
    )
    bandeira = models.CharField(max_length=20)
    ultimos_4_digitos = models.CharField(max_length=4)
    mes_validade = models.IntegerField()
    ano_validade = models.IntegerField()
    apelido = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: Cartão Principal")

    def __str__(self):
        return f"{self.bandeira} terminado em {self.ultimos_4_digitos}"

    class Meta:
        verbose_name = "Cartão de Crédito"
        verbose_name_plural = "Cartões de Crédito"


class Loja(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    prazo_retirada_dias = models.IntegerField(default=1)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.cidade}/{self.estado}"


class Carrinho(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrinho de {self.usuario.username}"
    
    def calcular_total(self):
        total = sum(item.calcular_subtotal() for item in self.itens.all())
        return total


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    def calcular_subtotal(self):
        return self.produto.preco * self.quantidade


class Pedido(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ('DOMICILIO', 'Entrega em Domicílio'),
        ('RETIRADA', 'Retirada na Loja'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_entrega = models.CharField(max_length=10, choices=TIPO_ENTREGA_CHOICES)
    
    # Campos para entrega em domicílio
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    # Campo para retirada na loja
    loja = models.ForeignKey(Loja, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pagamento
    cartao = models.ForeignKey(CartaoCredito, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Informações de entrega
    custo_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prazo_dias = models.IntegerField()
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.get_tipo_entrega_display()}"
    
    def calcular_subtotal_produtos(self):
        """Calcula o total dos produtos do pedido"""
        from decimal import Decimal
        total = sum(item.calcular_subtotal() for item in self.itens.all())
        return Decimal(str(total)) if total else Decimal('0')
    
    def calcular_total(self):
        """Calcula o valor total do pedido (produtos + entrega)"""
        return self.calcular_subtotal_produtos() + self.custo_entrega


class ItemPedido(models.Model):
    """Item de um pedido - cópia dos produtos do carrinho no momento da compra"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Preço no momento da compra
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Pedido #{self.pedido.id})"
    
    def calcular_subtotal(self):
        return self.preco_unitario * self.quantidade


