from django.db import migrations

def atualizar_imagens(apps, schema_editor):
    Produto = apps.get_model('mercadocesar', 'Produto')
    
    # Mapear códigos para Public IDs corretos do Cloudinary
    mapeamento = {
        'YPE-001': 'ypeclear_k2utb4',
        'PRA-001': 'arrozbrancocamil_d7lrh9',
        'CAM-001': 'feijaopretocamil_nlefpu',
        'ADR-001': 'adria_przoip',
    }
    
    for codigo, public_id in mapeamento.items():
        try:
            produto = Produto.objects.get(codigo=codigo)
            produto.imagem = public_id
            produto.save()
            print(f"✓ Atualizado {codigo}: {public_id}")
        except Produto.DoesNotExist:
            print(f"✗ Produto {codigo} não encontrado")

class Migration(migrations.Migration):

    dependencies = [
        ('mercadocesar', '0017_criar_produtos_iniciais'),
    ]

    operations = [
        migrations.RunPython(atualizar_imagens),
    ]
