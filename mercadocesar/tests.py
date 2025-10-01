from django.test import TestCase, TransactionTestCase
from decimal import Decimal
from .models import Produto, Armazem, Estoque
from django.db import IntegrityError, transaction

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
        
        with self.assertRaises(IntegrityError):
            produto2 = Produto.objects.create(
                codigo="ABC123",
                descricao="Produto-Teste",
                categoria="Categoria-Teste",
                preco_custo=Decimal('20.00'),
                preco_venda=Decimal('55.00'),
                unidade_medida="Unidade"
            )
    
    def test_campos_obrigatorios(self):
        """Testa se os campos obrigatórios estão sendo validados corretamente."""
        
        # Teste 1: codigo não pode ser vazio
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="",
                    descricao="Produto Teste 1",
                    categoria="Categoria Teste 1",
                    preco_custo=Decimal('10.00'),
                    preco_venda=Decimal('15.00'),
                    unidade_medida="unidade"
                )
        
        # Teste 2: descrição não pode ser vazia
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="Código Teste 1",
                    descricao="",
                    categoria="Categoria Teste 2",
                    preco_custo=Decimal('10.00'),
                    preco_venda=Decimal('15.00'),
                    unidade_medida="unidade"
                )
        
        # Teste 3: categoria não pode ser vazia
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="Código Teste 2",
                    descricao="Produto Teste 2",
                    categoria="",
                    preco_custo=Decimal('10.00'),
                    preco_venda=Decimal('15.00'),
                    unidade_medida="unidade"
                )
            
        # Teste 4: unidade_medida não pode ser None
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="Código Teste 3",
                    descricao="Produto Teste 3",
                    categoria="Categoria Teste 3",
                    preco_custo=Decimal('10.00'),
                    preco_venda=Decimal('15.00'),
                    unidade_medida=""
                )
        
        # Teste 5: preco_custo não pode ser None
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="Código Teste 4",
                    descricao="Produto Teste 4",
                    categoria="Categoria Teste 4",
                    preco_custo=None,
                    preco_venda=Decimal('15.00'),
                    unidade_medida="unidade"
                )
            
        # Teste 6: preco_venda não pode ser None
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Produto.objects.create(
                    codigo="Código Teste 5",
                    descricao="Produto Teste 5",
                    categoria="Categoria Teste 5",
                    preco_custo=Decimal('10.00'),
                    preco_venda=None,
                    unidade_medida="unidade"
                )  