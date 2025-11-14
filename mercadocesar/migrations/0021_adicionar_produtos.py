from django.db import migrations
from decimal import Decimal

def create_produtos(apps, schema_editor):
    Produto = apps.get_model('mercadocesar', 'Produto')
    
    # Lista de produtos: (nome, codigo, categoria, imagem)
    # Public IDs do Cloudinary 
    produtos = [
        ('Pepsi', 'PEP-001', 'Bebidas', 'pepsi_mxkk3f'),
        ('Chocolate Diamante Negro', 'DIA-001', 'Alimentos', 'diamantenegro_wxuhwh'),
        ('Café Tradicional 3 Corações', 'COR-001', 'Bebidas', 'cafetrad3cor_qnpa7b'),
        ('Refrigerante H2OH', 'HOH-001', 'Bebidas', 'h2ohlimao_krhz2n'),
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
            print(f"Produto '{nome}' já existe.")

class Migration(migrations.Migration):

    dependencies = [
        ('mercadocesar', '0020_mudar_para_cloudinary_field'),
    ]

    operations = [
        migrations.RunPython(create_produtos),
    ]
