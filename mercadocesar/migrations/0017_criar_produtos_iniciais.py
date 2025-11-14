from django.db import migrations
from decimal import Decimal

def create_produtos(apps, schema_editor):
    Produto = apps.get_model('mercadocesar', 'Produto')
    
    # Lista de produtos: (nome, codigo, categoria, imagem)
    produtos = [
        ('Detergente Ypê Clear', 'YPE-001', 'Limpeza', 'product_images/ypeclear_k2utb4'),
        ('Arroz Prato Fino', 'PRA-001', 'Alimentos', 'product_images/arrozbrancocamil_d7lrh9'),
        ('Feijão Preto Camil', 'CAM-001', 'Alimentos', 'product_images/feijaopretocamil_nlefpu'),
        ('Macarrão Adria', 'ADR-001', 'Alimentos', 'product_images/adria_przoip'),
    ]
    
    for nome, codigo, categoria, imagem in produtos:
        obj, created = Produto.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': nome,
                'categoria': categoria,
                'imagem': imagem,              
                'descricao': nome,
                'preco_custo': Decimal('1.00'),
                'preco': Decimal('1.00'),
                'unidade_medida': 'unidade'
            }
        )
        
        if created:
            print(f"Produto '{nome}' criado com sucesso.")
        else:
            print(f"ℹProduto '{nome}' já existe.")

class Migration(migrations.Migration):

    dependencies = [
        ('mercadocesar', '0016_produto_imagem'),
    ]

    operations = [
        migrations.RunPython(create_produtos),
    ]
