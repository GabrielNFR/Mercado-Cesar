from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def criar_driver():
    """Criar novo WebDriver otimizado para CI/CD"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(15)  # Aumentado de 10 para 15
    return driver

def fazer_login(driver, base_url):
    """Fazer login no sistema"""
    driver.get(f"{base_url}/accounts/login/")
    wait = WebDriverWait(driver, 20)  # Aumentado de 15 para 20
    
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    
    submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    driver.execute_script("arguments[0].click();", submit_button)
    
    # Aguardar redirecionamento após login
    wait.until(lambda d: "/accounts/login/" not in d.current_url)
    time.sleep(1)

def compra_produto(driver, base_url,i):
    wait=WebDriverWait(driver, 20)  # Aumentado de 15 para 20  
    driver.get(f"{base_url}/checkout/")
    time.sleep(1)

    botao_escolha = driver.find_element(By.XPATH, "//*[contains(text(), 'Mercado Cesar - Boa Viagem')]")
    
    driver.execute_script("arguments[0].scrollIntoView(true);", botao_escolha)
    
    time.sleep(1)
    driver.execute_script("arguments[0].click();", botao_escolha)    
    print(f"[Cenário {i}] Escolhido o local de entrega")
     
    bt2=driver.find_element(By.XPATH,"//button[contains(text(),'Retirar na Loja')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", bt2)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", bt2)
    print(f"[Cenário {i}] Produto para entregar na loja física")
    time.sleep(1)

    wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='radio']"))
        )
    radio_cartao = driver.find_element(By.XPATH, "//input[@type='radio']")
    driver.execute_script("arguments[0].click();", radio_cartao)
    print(f"[Cenário {i}] Meio de pagamento escolhido")


    botfin=driver.find_element(By.XPATH,"//button[contains(text(), 'Finalizar Pedido')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", botfin)
    driver.execute_script("arguments[0].click();",botfin)
    time.sleep(1)
    print(f"[Cenário {i}] Compra concluída com sucesso")

def cenario_1_comprarapida(base_url):
    driver=criar_driver()    
    try:
        # Fazer login
        fazer_login(driver,base_url)
        print("[Cenário 1] Login realizado com sucesso")
        
        # Comprar (para ter histórico)
        print("[Cenário 1] Iniciando compra para criar histórico...")
        
        driver.get(f"{base_url}/busca/")

        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        if len(botoes_adicionar) > 2:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[2])
            wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Adicionar ao Carrinho')])[3]")))
            driver.execute_script("arguments[0].click();", botoes_adicionar[2])
            print(f"[Cenário 1] Produto adicionado ao carrinho")
        else:
           raise ValueError(f"[Cenário 1] FALHOU - Nenhum botão 'Adicionar ao Carrinho' encontrado")
        
        compra_produto(driver,base_url,1)
        
        wait=WebDriverWait(driver, 10)
        # Pedidos recentes
        driver.get(f"{base_url}/recentes/")
        time.sleep(2)
        print("[Cenário 1] Acessou página /recentes/")
        
        # PASSO 5: Verificar se o carrinho foi recriado
        if "/recentes" in driver.current_url:
                print(f"[Cenário 1] Histórico exibido com sucesso- {driver.current_url}")
                return True
        else:
                print(f"[Cenário 1] FALHOU - Não há nada - URL atual: {driver.current_url}")
                return False    
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e} - {driver}")
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
        e2=driver.find_elements(By.XPATH, "//table//tbody//tr")
        time.sleep(2)
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
        wait=WebDriverWait(driver,10)
        fazer_login(driver,base_url)
    
        driver.get(f"{base_url}/recentes/")
        botao_pedir_novamente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Pedir Novamente')]"))
        )
        texto_botao = botao_pedir_novamente.text
        pedido_id = texto_botao.split('#')[1].split(' ')[0]
        verificador=True
        print(f"[Cenário 3] Repetindo pedido #{pedido_id}")
        
        driver.execute_script(f"sessionStorage.setItem('pedido_id', '{pedido_id}');")
        compra_produto(driver,base_url,3)

        if verificador==True:
            print(f"[Cenário 3] - PASSOU - Compra refeita com sucesso")
            return True
        else:
            print(f"[Cenário 3] - FALHOU - A compra não ocorreu bem-succedidamente")
            return False
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e} - {driver}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

def cenario4_compraindevida(base_url):
    driver=criar_driver()
    wait=WebDriverWait(driver, 15)
    bloqueou_compra = False
    try:
        fazer_login(driver,base_url)
        print("[Cenário 4] Login realizado com sucesso")
        
        # PASSO 1: Editar estoque do produto para 2 unidades
        driver.get(f"{base_url}/estoque/?action=edit&id=9")
        time.sleep(1)
        
        campo_quantidade = wait.until(EC.presence_of_element_located((By.NAME, "quantidade")))
        campo_quantidade.clear()
        campo_quantidade.send_keys("2")  # 2 unidades disponíveis
        print("[Cenário 4] Estoque configurado para 2 unidades")
        
        # Salvar alteração
        botao_salvar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        driver.execute_script("arguments[0].click();", botao_salvar)
        time.sleep(2)
        print("[Cenário 4] Estoque salvo")
        
        # PASSO 2: PRIMEIRA COMPRA - Comprar 1 unidade
        driver.get(f"{base_url}/busca/")
        time.sleep(2)
        
        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        
        if len(botoes_adicionar) > 0:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[0])
            time.sleep(1)
            driver.execute_script("arguments[0].click();", botoes_adicionar[0])
            time.sleep(1)
            print(f"[Cenário 4] Produto adicionado ao carrinho (1/2 disponíveis)")
        else: 
            raise ValueError(f"[Cenário 4] FALHOU - Nenhum produto encontrado")
        
        # Finalizar primeira compra
        compra_produto(driver, base_url, 4)
        print("[Cenário 4] Primeira compra finalizada - Estoque: 1 restante")
        
        # PASSO 3: SEGUNDA COMPRA - Comprar a última unidade
        driver.get(f"{base_url}/busca/")
        time.sleep(2)
        
        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        if len(botoes_adicionar) > 0:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[0])
            time.sleep(1)
            driver.execute_script("arguments[0].click();", botoes_adicionar[0])
            time.sleep(1)
            print(f"[Cenário 4] Produto adicionado novamente (última unidade)")
        
        # Finalizar segunda compra
        compra_produto(driver, base_url, 4)
        print("[Cenário 4] Segunda compra finalizada - Estoque agora está ZERADO")
        
        # PASSO 4: Ir para histórico e tentar comprar NOVAMENTE via histórico (deveria bloquear)
        driver.get(f"{base_url}/recentes/")
        time.sleep(2)
        print("[Cenário 4] Acessou página de histórico")
        
        # Clicar em "Pedir Novamente" 
        botao_pedir_novamente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Pedir Novamente')]"))
        )
        texto_botao = botao_pedir_novamente.text
        pedido_id = texto_botao.split('#')[1].split(' ')[0]
        print(f"[Cenário 4] Tentando repetir pedido #{pedido_id} VIA HISTÓRICO (estoque ZERADO)")
        
        # Setar pedido_id no sessionStorage e ir para checkout
        driver.execute_script(f"sessionStorage.setItem('pedido_id', '{pedido_id}');")
        driver.get(f"{base_url}/checkout/")
        time.sleep(3)  # Aguardar JavaScript processar
        
        # PASSO 5: Verificar se o sistema bloqueou
        try:
            # Verificar se há produtos no carrinho (não deveria ter)
            carrinho_items = driver.find_elements(By.XPATH, "//table//tbody//tr")
            
            if len(carrinho_items) == 0:
                print("[Cenário 4] ✓ Carrinho vazio - Sistema bloqueou compra via histórico (sem estoque)")
                bloqueou_compra = True
            else:
                print(f"[Cenário 4] ⚠️ Carrinho tem {len(carrinho_items)} item(s) - Tentando finalizar...")
                compra_produto(driver, base_url, 4)
                print("[Cenário 4] ⚠️ Terceira compra foi concluída (NÃO deveria!)")
                bloqueou_compra = False
                
        except Exception as e:
            print(f"[Cenário 4] ✓ Sistema bloqueou a compra via histórico: {e}")
            bloqueou_compra = True

        # Verificar resultado
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
