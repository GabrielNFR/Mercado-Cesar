from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.validators import MinValueValidator


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


