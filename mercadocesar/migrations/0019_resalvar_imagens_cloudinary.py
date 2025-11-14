from django.db import migrations

def resalvar_produtos_com_imagem(apps, schema_editor):
    """
    Re-salva produtos com imagens para forçar o Django a usar MediaCloudinaryStorage.
    Quando os produtos foram criados inicialmente, o DEFAULT_FILE_STORAGE não estava configurado,
    então o Django salvou os valores como caminhos de arquivo local.
    """
    Produto = apps.get_model('mercadocesar', 'Produto')
    
    produtos_com_imagem = Produto.objects.filter(imagem__isnull=False).exclude(imagem='')
    
    print(f"\n[CLOUDINARY MIGRATION] Forçando re-save de {produtos_com_imagem.count()} produtos com imagem...")
    
    for produto in produtos_com_imagem:
        # Pegar o valor atual (Public ID)
        imagem_atual = produto.imagem.name if produto.imagem else None
        
        if imagem_atual:
            # Re-atribuir o mesmo valor e salvar
            # Isso força o Django a processar através do MediaCloudinaryStorage configurado
            produto.imagem = imagem_atual
            produto.save(update_fields=['imagem'])
            print(f"✓ Re-salvou {produto.codigo}: {imagem_atual}")

class Migration(migrations.Migration):

    dependencies = [
        ('mercadocesar', '0018_atualizar_imagens_cloudinary'),
    ]

    operations = [
        migrations.RunPython(resalvar_produtos_com_imagem),
    ]
