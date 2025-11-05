from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def criar_driver():
    """Criar novo WebDriver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver

def fazer_login(driver, base_url):
    """Fazer login no sistema"""
    driver.get(f"{base_url}/accounts/login/")
    wait = WebDriverWait(driver, 10)

    
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    
    submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
    driver.execute_script("arguments[0].click();", submit_button)
    time.sleep(2)

def compra_produto(driver, base_url):
    wait=WebDriverWait(driver, 10)
    driver.get(f"{base_url}/busca/")
    try:
        item_a_comprar=driver.find_elements(By.NAME, "Adicionar ao carrinho")
        indice=2
        if len(item_a_comprar) > indice:
            botao_especifico = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"(//button)[{indice + 1}]"))
            )
            botao_especifico.click()
            print(f"Botão no índice {indice} clicado com sucesso.")
        else:
            print(f"Não foi possível encontrar um botão no índice {indice}.")

        driver.find_element(By.NAME,"Finalizar compra")
        EC.element_to_be_clickable((By.XPATH, f"(//button)[{indice + 1}]"))

    except Exception as e:
        print(f"Ocorreu um erro: {e} - {driver} - {base_url}")
    finally:
        driver.quit()    

def cenario_1_comprarapida_incompleta(base_url):
    driver=criar_driver()
    wait=WebDriverWait(driver, 10)
    
    try:
        # Fazer login
        driver.get(f"{base_url}/accounts/login/")
        
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(2)
        print("[Cenário 1] Login realizado com sucesso")
        
        # Comprar (para ter histórico)
        print("[Cenário 1] Iniciando compra para criar histórico...")
        driver.get(f"{base_url}/busca/")
        time.sleep(2)
        
        # Adicionar produto ao carrinho
        botoes_adicionar = driver.find_elements(By.XPATH, "//button[contains(text(), 'Adicionar ao Carrinho')]")
        if len(botoes_adicionar) > 2:
            driver.execute_script("arguments[0].scrollIntoView(true);", botoes_adicionar[2])
            time.sleep(1)
            driver.execute_script("arguments[0].click();", botoes_adicionar[2])
            print("[Cenário 1] Produto adicionado ao carrinho")
        else:
            raise ValueError("[Cenário 1] FALHOU - Nenhum botão 'Adicionar ao Carrinho' encontrado")
        
        
        driver.get(f"{base_url}/checkout/")
        time.sleep(2)  # Aguardar página carregar
        botao_escolha = driver.find_element(By.XPATH, "//*[contains(text(), 'Mercado Cesar - Boa Viagem')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_escolha)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", botao_escolha)
        print("[Cenário 1] Escolhido o local de entrega")


        bt2=driver.find_element(By.XPATH,"//button[contains(text(),'Retirar na Loja')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", bt2)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", bt2)
        print("[Cenário 1] Produto para entregar na loja física")
        time.sleep(2)


        radio_cartao = driver.find_element(By.XPATH, "//input[@type='radio']")
        driver.execute_script("arguments[0].scrollIntoView(true);", radio_cartao)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", radio_cartao)
        print("[Cenário 1] Meio de pagamento escolhido")


        botfin=driver.find_element(By.XPATH,"//button[contains(text(), 'Finalizar Pedido')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", botfin)
        driver.execute_script("arguments[0].click()",botfin)
        time.sleep(2)
        print("[Cenário 1] Compra concluída com sucesso")        
        
        # Pedidos recentes
        driver.get(f"{base_url}/recentes/")
        time.sleep(2)
        print("[Cenário 1] Acessou página /recentes/")
        
        # PASSO 4: Usar o sistema de compra rápida (sessionStorage)
        botao_pedir_novamente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Pedir Novamente')]"))
        )
        
        # Extrair o ID do pedido do texto do botão (ex: "Pedido #27 - Pedir Novamente")
        texto_botao = botao_pedir_novamente.text
        pedido_id = texto_botao.split('#')[1].split(' ')[0]
        print(f"[Cenário 1] Repetindo pedido #{pedido_id}")
        
        # Setar pedido_id no sessionStorage e navegar para checkout
        driver.execute_script(f"sessionStorage.setItem('pedido_id', '{pedido_id}');")
        driver.get(f"{base_url}/checkout/")
        print("[Cenário 1] Aguardando sistema de compra rápida processar...")
        
        # Aguardar o AJAX criar o carrinho e a página recarregar
        wait_longo = WebDriverWait(driver, 10)
        wait_longo.until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody//tr"))
        )

        # PASSO 5: Verificar se o carrinho foi recriado
        if "/checkout/" in driver.current_url:
            carrinho_items = driver.find_elements(By.XPATH, "//table//tbody//tr")
            if len(carrinho_items) > 0:
                print(f"[Cenário 1] PASSOU - Carrinho recriado com {len(carrinho_items)} item(ns)")
                return True
            else:
                print("[Cenário 1] FALHOU - Carrinho está vazio")
                return False
        else:
            print(f"[Cenário 1] FALHOU - URL atual: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e} - {driver}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()
    
def cenario2_compravelha_feita(base_url):
    driver=criar_driver()
   
    wait=WebDriverWait(driver, 3)

    try:
        driver.get(f"{base_url}/accounts/login/")
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(2)
        print("[Cenário 2] Login realizado com sucesso")
    
        driver.get(f"{base_url}/recentes/")

        bot_ant=driver.find_element(By.XPATH, "//a[contains(text(), 'Pedir Novamente')]")
        driver.execute_script("arguments[0].scrollIntoView(true);",bot_ant)
        driver.execute_script("arguments[0].click();", bot_ant)

        time.sleep(2)  # Aguardar página carregar
        botao1 = driver.find_element(By.XPATH, "//*[contains(text(), 'Mercado Cesar - Boa Viagem')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", botao1)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", botao1)
        print("[Cenário 2] Escolhido o local de entrega")

        botao2=driver.find_element(By.XPATH,"//button[contains(text(),'Retirar na Loja')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", botao2)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", botao2)
        print("[Cenário 2] Produto para entregar na loja física")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='radio']"))
        )
        radio = driver.find_element(By.XPATH, "//input[@type='radio']")
        driver.execute_script("arguments[0].click",radio)

        botao4=driver.find_element(By.XPATH,"//button[contains(text(), 'Finalizar Pedido')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", botao4)
        driver.execute_script("arguments[0].click()",botao4)
        time.sleep(2)
        print("[Cenário 2] Compra concluída com sucesso")
        return True

    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e} - {driver}")
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
        cenario_1_comprarapida_incompleta(base_url),   
        cenario2_compravelha_feita(base_url),
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
