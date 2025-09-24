from django.db import models


class Produto(models.Model):
	codigo = models.CharField(max_length=30, unique=True)
	descricao = models.CharField(max_length=200, blank=True, default="")
	categoria = models.CharField(max_length=50)
	preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
	preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
	unidade_medida = models.CharField(max_length=20)

	def __str__(self):
		return f"{self.codigo} - {self.descricao} - {self.categoria}"


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

