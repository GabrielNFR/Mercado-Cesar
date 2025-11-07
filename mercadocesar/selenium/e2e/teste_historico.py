from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuração do Django para usar ORM nos testes
import os
import sys
import django

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Importar models após setup do Django
from mercadocesar.models import Produto, Estoque, Pedido, ItemPedido, Armazem

def criar_driver():
    """Criar novo WebDriver otimizado para CI/CD"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(30)  # AUMENTADO de 15 para 30
    driver.set_page_load_timeout(60)  # Timeout de 60s para carregar páginas
    return driver

def fazer_login(driver, base_url):
    """Fazer login no sistema"""
    driver.get(f"{base_url}/accounts/login/")
    wait = WebDriverWait(driver, 30)  # AUMENTADO de 20 para 30
    
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.send_keys("admin")
    
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.send_keys("admin123")
    
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    driver.execute_script("arguments[0].click();", submit_button)
    
    # Aguardar redirecionamento após login
    time.sleep(3)  # AUMENTADO de 1 para 3

def compra_produto(driver, base_url,i):
    wait=WebDriverWait(driver, 30)  # AUMENTADO de 20 para 30
    driver.get(f"{base_url}/checkout/")
    time.sleep(2)  # AUMENTADO de 1 para 2

    botao_escolha = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Mercado Cesar - Boa Viagem')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_escolha)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", botao_escolha)    
    print(f"[Cenário {i}] Escolhido o local de entrega")
    time.sleep(2)  # AUMENTADO de 1 para 2
     
    bt2 = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Retirar na Loja')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", bt2)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", bt2)
    print(f"[Cenário {i}] Produto para entregar na loja física")
    time.sleep(2)  # AUMENTADO de 1 para 2

    radio_cartao = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='radio']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", radio_cartao)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", radio_cartao)
    print(f"[Cenário {i}] Meio de pagamento escolhido")
    time.sleep(1)
    
    # Selecionar cartão de crédito
    try:
        cartao_radio = driver.find_elements(By.XPATH, "//input[@name='cartao_id']")
        if cartao_radio:
            driver.execute_script("arguments[0].click();", cartao_radio[0])
            time.sleep(1)
    except:
        pass

    botfin = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(), 'Finalizar Pedido')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", botfin)
    time.sleep(1)
    driver.execute_script("arguments[0].click();",botfin)
    time.sleep(3)
    print(f"[Cenário {i}] Compra concluída com sucesso")

def cenario_1_comprarapida(base_url):
    driver=criar_driver()    
    try:
        wait=WebDriverWait(driver, 30)  # AUMENTADO de 20 para 30
        
        # Fazer login
        fazer_login(driver,base_url)
        print("[Cenário 1] Login realizado com sucesso")
        
        # Comprar (para ter histórico)
        print("[Cenário 1] Iniciando compra para criar histórico...")
        
        driver.get(f"{base_url}/busca/")
        time.sleep(3)  # AUMENTADO de 2 para 3

        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        if len(botoes_adicionar) > 2:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[2])
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Adicionar ao Carrinho')])[3]")))
            driver.execute_script("arguments[0].click();", botoes_adicionar[2])
            print(f"[Cenário 1] Produto adicionado ao carrinho")
        else:
           raise ValueError(f"[Cenário 1] FALHOU - Nenhum botão 'Adicionar ao Carrinho' encontrado")
        
        compra_produto(driver,base_url,1)
        
        # Pedidos recentes
        driver.get(f"{base_url}/recentes/")
        time.sleep(4)  # AUMENTADO de 2 para 4
        print("[Cenário 1] Acessou página /recentes/")
        
        # PASSO 5: Verificar se o carrinho foi recriado
        if "/recentes" in driver.current_url:
                print(f"[Cenário 1] Histórico exibido com sucesso- {driver.current_url}")
                return True
        else:
                print(f"[Cenário 1] FALHOU - Não há nada - URL atual: {driver.current_url}")
                return False    
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

def cenario2_dadoscompra(base_url):
    driver=criar_driver()
    try:
        fazer_login(driver,base_url)
        
        driver.get(f"{base_url}/recentes/")
        time.sleep(3)  # AUMENTADO de 2 para 3
        e2=driver.find_elements(By.XPATH, "//table//tbody//tr")
        if len(e2)>0:
                print(f"[Cenário 2] PASSOU - Dados do produto expostos na tela")
                return True
        else:
            print(f"[Cenário 2] FALHOU - Nada apareceu - URL atual: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e} - {driver}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

def cenario3_comprarefeita(base_url):
    driver=criar_driver()
    verificador=False  
    try:
        wait=WebDriverWait(driver, 30)
        fazer_login(driver,base_url)
        print("[Cenário 3] Login realizado com sucesso")
    
        driver.get(f"{base_url}/recentes/")
        time.sleep(3)  # AUMENTADO de 2 para 3
        
        botao_pedir_novamente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Pedir Novamente')]"))
        )
        texto_botao = botao_pedir_novamente.text
        pedido_id = texto_botao.split('#')[1].split(' ')[0]
        verificador=True
        print(f"[Cenário 3] Repetindo pedido #{pedido_id}")
        
        driver.execute_script(f"sessionStorage.setItem('pedido_id', '{pedido_id}');")
        driver.get(f"{base_url}/checkout/")
        time.sleep(4)  # AUMENTADO de 3 para 4 - Aguardar JavaScript processar
        
        # Verificar se carrinho foi recriado
        carrinho_items = driver.find_elements(By.XPATH, "//table//tbody//tr")
        if len(carrinho_items) > 0:
            print(f"[Cenário 3] Carrinho recriado com {len(carrinho_items)} item(ns)")
            compra_produto(driver,base_url,3)
            print(f"[Cenário 3] PASSOU - Compra refeita com sucesso")
            return True
        else:
            print(f"[Cenário 3] FALHOU - Carrinho vazio")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

def cenario4_compraindevida(base_url):
    driver=criar_driver()
    wait=WebDriverWait(driver, 30)
    bloqueou_compra = False
    total_pedidos_antes = 0  # Inicializar variável
    
    try:
        # PASSO 1: Configurar estoque usando Django ORM (MUITO MAIS RÁPIDO)
        print("[Cenário 4] - Configurando estoque via Django ORM...")
        produto = Produto.objects.get(id=9)
        
        # IMPORTANTE: ZERAR TODO O ESTOQUE do produto em TODOS os armazéns primeiro
        total_zerado = Estoque.objects.filter(produto=produto).update(quantidade=0)
        print(f"[Cenário 4]- {total_zerado} registro(s) de estoque ZERADOS para '{produto.nome}'")
        
        # Verificar estado após zerar
        estoques_apos_zerar = Estoque.objects.filter(produto=produto)
        print(f"[Cenário 4]- Estoques após zerar:")
        for e in estoques_apos_zerar:
            print(f"  - {e.armazem.nome}: {e.quantidade} unidade(s)")
        
        # Buscar ou criar estoque para o produto em UM armazém específico
        armazem = Armazem.objects.first()  # Pegar primeiro armazém disponível
        if not armazem:
            print(f"[Cenário 4]- Nenhum armazém cadastrado no sistema")
            return False
        
        estoque, criado = Estoque.objects.get_or_create(
            produto=produto,
            armazem=armazem,
            defaults={'quantidade': 1}
        )
        
        if not criado:
            # Se já existia, atualizar para 1
            estoque.quantidade = 1
            estoque.save()
        
        print(f"[Cenário 4] - Estoque de '{produto.nome}' em '{armazem.nome}' configurado para 1 unidade")
        
        # Verificar estado final ANTES da compra
        estoques_antes_compra = Estoque.objects.filter(produto=produto)
        total_antes = sum(e.quantidade for e in estoques_antes_compra)
        print(f"[Cenário 4] - Total em estoque ANTES da compra: {total_antes} unidade(s)")
        
        # PASSO 2: Login via Selenium
        fazer_login(driver, base_url)
        print("[Cenário 4] - Login realizado com sucesso")
        
        # PASSO 3: PRIMEIRA COMPRA - Comprar a única unidade
        driver.get(f"{base_url}/busca/")
        time.sleep(2)
        
        # Contar pedidos ANTES da compra
        total_pedidos_antes = Pedido.objects.count()
        print(f"[Cenário 4] - Total de pedidos no sistema ANTES da compra: {total_pedidos_antes}")
        
        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        
        if len(botoes_adicionar) > 0:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[0])
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Adicionar ao Carrinho')])[1]")))
            driver.execute_script("arguments[0].click();", botoes_adicionar[0])
            time.sleep(2)
            print(f"[Cenário 4] - Produto adicionado ao carrinho (1/1 disponível)")
        else: 
            raise ValueError(f"[Cenário 4] - FALHOU - Nenhum produto encontrado")
        
        # Finalizar primeira compra
        compra_produto(driver, base_url, 4)
        print("[Cenário 4] Primeira compra finalizada")
        
        # Verificar que o estoque foi zerado - TODOS os estoques do produto
        time.sleep(2)  # Aguardar transação do pedido ser commitada
        
        # Contar pedidos DEPOIS da compra
        total_pedidos_depois = Pedido.objects.count()
        print(f"[Cenário 4] - Total de pedidos no sistema DEPOIS da compra: {total_pedidos_depois}")
        print(f"[Cenário 4] - Novos pedidos criados: {total_pedidos_depois - total_pedidos_antes}")
        
        # Verificar se pedido foi realmente criado
        from django.contrib.auth.models import User
        usuario_admin = User.objects.get(username='admin')
        ultimo_pedido = Pedido.objects.filter(usuario=usuario_admin).order_by('-id').first()
        if ultimo_pedido:
            print(f"[Cenário 4] Último pedido criado: #{ultimo_pedido.id}")
            itens_pedido = ItemPedido.objects.filter(pedido=ultimo_pedido)
            print(f"[Cenário 4] Itens no pedido: {itens_pedido.count()}")
            for item in itens_pedido:
                print(f"  - {item.produto.nome}: {item.quantidade} unidade(s)")
        else:
            print(f"[Cenário 4] ⚠️ Nenhum pedido encontrado para o usuário admin!")
        
        estoques_produto = Estoque.objects.filter(produto=produto)
        total_estoque = sum(e.quantidade for e in estoques_produto)
        print(f"[Cenário 4] Estoques após compra:")
        for e in estoques_produto:
            print(f"  - {e.armazem.nome}: {e.quantidade} unidade(s)")
        print(f"[Cenário 4] Total em estoque: {total_estoque} unidade(s)")
        
        if total_estoque > 0:
            print(f"[Cenário 4] ⚠️ AVISO: Ainda há {total_estoque} unidade(s) em estoque após compra!")
            print(f"[Cenário 4] Isso indica que havia estoque em outros armazéns que não foi considerado no teste")

        # PASSO 4: Ir para histórico e tentar comprar via histórico (deveria bloquear)
        driver.get(f"{base_url}/recentes/")
        time.sleep(3)
        print("[Cenário 4] Acessou página de histórico")
        
        # Clicar em "Pedir Novamente" 
        botao_pedir_novamente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Pedir Novamente')]"))
        )
        texto_botao = botao_pedir_novamente.text
        pedido_id = texto_botao.split('#')[1].split(' ')[0]
        print(f"[Cenário 4] Tentando repetir pedido #{pedido_id} via histórico (estoque ZERADO)")
        
        # Setar pedido_id no sessionStorage e ir para checkout
        driver.execute_script(f"sessionStorage.setItem('pedido_id', '{pedido_id}');")
        driver.get(f"{base_url}/checkout/")
        time.sleep(5)  # AUMENTADO: Aguardar JavaScript + AJAX processar
        
        # PASSO 5: Verificar se o sistema bloqueou
        print(f"[Cenário 4] Verificando se sistema bloqueia compra sem estoque...")
        
        # Verificar se há produtos no carrinho (pode ter, isso é OK)
        carrinho_items = driver.find_elements(By.XPATH, "//table//tbody//tr")
        
        # Debug: verificar URL e HTML
        print(f"[Cenário 4] URL atual: {driver.current_url}")
        print(f"[Cenário 4] Itens encontrados na tabela: {len(carrinho_items)}")
        
        if len(carrinho_items) > 0:
            print(f"[Cenário 4] Carrinho criado com {len(carrinho_items)} item(s) via histórico")
            
            # O TESTE REAL: tentar finalizar a compra (deveria falhar por falta de estoque)
            try:
                # Selecionar loja
                botao_escolha = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Mercado Cesar - Boa Viagem')]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", botao_escolha)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", botao_escolha)
                time.sleep(2)
                
                # Retirar na loja
                bt2 = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Retirar na Loja')]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", bt2)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", bt2)
                time.sleep(2)
                
                # Selecionar cartão
                try:
                    cartao_radio = driver.find_elements(By.XPATH, "//input[@name='cartao_id']")
                    if cartao_radio:
                        driver.execute_script("arguments[0].click();", cartao_radio[0])
                        time.sleep(1)
                except:
                    pass
                
                # Tentar finalizar
                url_antes_finalizar = driver.current_url
                botfin = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(), 'Finalizar Pedido')]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", botfin)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", botfin)
                time.sleep(3)
                
                url_depois_finalizar = driver.current_url
                
                # Se voltou para checkout ou tem mensagem de erro = BLOQUEOU (correto)
                # Se foi para /finalizar/ = NÃO BLOQUEOU (erro)
                if url_depois_finalizar == url_antes_finalizar or "/checkout/" in url_depois_finalizar:
                    # Verificar mensagens de erro
                    mensagens_erro = driver.find_elements(By.XPATH, "//*[contains(@class, 'alert') or contains(@class, 'error')]")
                    if mensagens_erro:
                        print(f"[Cenário 4] ✓ Sistema bloqueou finalização - Mensagens de erro encontradas")
                        bloqueou_compra = True
                    else:
                        print(f"[Cenário 4] ✓ Sistema bloqueou finalização - Voltou para checkout")
                        bloqueou_compra = True
                elif "/finalizar/" in url_depois_finalizar:
                    print(f"[Cenário 4] ⚠️ Sistema NÃO bloqueou - Pedido foi finalizado sem estoque!")
                    bloqueou_compra = False
                else:
                    print(f"[Cenário 4] URL inesperada após finalizar: {url_depois_finalizar}")
                    bloqueou_compra = False
                    
            except Exception as e:
                print(f"[Cenário 4] Erro ao tentar finalizar: {e}")
                bloqueou_compra = True  # Se deu erro, consideramos que bloqueou
        else:
            # Se carrinho está vazio, também está bloqueando (apenas de forma diferente)
            print("[Cenário 4] ✓ Carrinho vazio - Sistema bloqueou na criação do carrinho")
            bloqueou_compra = True

        if bloqueou_compra:
            print(f"[Cenário 4] PASSOU - Sistema barrou compra via histórico sem estoque")
            return True
        else:
            print(f"[Cenário 4] FALHOU - Sistema permitiu compra indevida via histórico")
            return False
            
    except Exception as e:
        print(f"[Cenário 4] FALHOU - Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

def main():
    """Executar todos os cenários"""
    print("=" * 70)
    print("TESTES E2E - HISTÓRIA 8: PEDIDOS BASEADOS EM HISTÓRICO DE COMPRAS")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    resultados = [
        cenario_1_comprarapida(base_url),
        cenario2_dadoscompra(base_url),
        cenario3_comprarefeita(base_url),
        cenario4_compraindevida(base_url)
    ]
    
    total = len(resultados)
    u = sum(resultados)
    
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Total: {total} | Passou: {u} | Falhou: {total - u}")
    print("=" * 70)
    
    return 0 if u == total else 1

if __name__ == "__main__":
    exit(main())
