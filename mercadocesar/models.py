from django.db import models


class Produto(models.Model):
	codigo = models.CharField(max_length=30, unique=True)
	categoria = models.CharField(max_length=50)
	preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
	preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
	unidade_medida = models.CharField(max_length=20)

	def __str__(self):
		return f"{self.codigo} - {self.categoria}"

