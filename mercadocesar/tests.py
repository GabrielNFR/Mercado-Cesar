from django.test import TestCase
from decimal import Decimal
from .models import Produto, Armazem, Estoque

class ProdutoModelTest(TestCase):
    """Testes para o modelo Produto."""

    def test_criacao_produto(self):
        """Testa se um produto é criado corretamente."""
        produto  = Produto.objects.create(
            codigo="ABC123",
            descricao="Produto de Teste",
            categoria="Categoria Teste",
            preco_custo=Decimal('10.00'),
            preco_venda=Decimal('15.00'),
            unidade_medida="unidade"
        )
        
        # Verificar se o produto foi salvo corretamente
        self.assertEqual(produto.codigo, "ABC123")
        self.assertEqual(produto.descricao, "Produto de Teste")
        self.assertEqual(produto.categoria, "Categoria Teste")
        self.assertEqual(produto.preco_custo, Decimal('10.00'))
        self.assertEqual(produto.preco_venda, Decimal('15.00'))
        
        # Verificar se o método __str__ funciona corretamente
        self.assertEqual(str(produto), "ABC123 - Produto de Teste - Categoria Teste")
        
        # Verificar se o produto foi salvo no banco de dados
        produto_salvo = Produto.objects.get(codigo="ABC123")
        self.assertEqual(produto_salvo.descricao, "Produto de Teste")
        
    def test_codigo_unico(self):
        """Testa se o código do produto é único."""
        
        # Criar o primeiro produto com um código específico
        Produto.objects.create(
            codigo="UNICO123",
            descricao="Produto Único",
            categoria="Categoria Única",
            preco_custo=Decimal('20.00'),
            preco_venda=Decimal('30.00'),
            unidade_medida="unidade"
        )
        
        # Tentar criar um segundo produto com o mesmo código pra ver se dá erro
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                codigo="UNICO123",  
                descricao="Outro Produto",
                categoria="Outra Categoria",
                preco_custo=Decimal('25.00'),
                preco_venda=Decimal('35.00'),
                unidade_medida="unidade"
            )
    
    def test_descricao_unico(self):
        """Testa se o produto não foi criado de forma duplicada"""       
        produto1  = Produto.objects.create(
            codigo="ABC321",
            descricao="Produto-Teste",
            categoria="Categoria-Teste",
            preco_custo=Decimal('20.00'),
            preco_venda=Decimal('55.00'),
            unidade_medida="Unidade"
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):

         produto2 = Produto.objects.create(
            codigo="ABC123",
            descricao="Produto-Teste",
            categoria="Categoria-Teste",
            preco_custo=Decimal('20.00'),
            preco_venda=Decimal('55.00'),
            unidade_medida="Unidade"
        )
         
        