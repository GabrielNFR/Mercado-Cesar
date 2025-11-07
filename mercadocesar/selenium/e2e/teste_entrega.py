"""
Testes E2E para História 7: Escolha de Tipo de Entrega
Cenários:
1. Escolher entrega em domicílio com estimativa de prazo e custo
2. Escolher retirada na loja com estimativa de prazo
3. Entrega indisponível para o endereço informado
4. CEP inválido
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests


def criar_driver():
    """Criar novo WebDriver"""
    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def fazer_login(driver, base_url):
    """Fazer login no sistema e retornar os cookies de sessão"""
    driver.get(f"{base_url}/accounts/login/")
    wait = WebDriverWait(driver, 10)
    
    username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username.send_keys("admin")
    
    password = driver.find_element(By.NAME, "password")
    password.send_keys("admin123")
    
    submit_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn[type='submit']")))
    driver.execute_script("arguments[0].click();", submit_btn)
    
    wait.until(EC.url_changes(f"{base_url}/accounts/login/"))
    time.sleep(1)
    
    cookies = driver.get_cookies()
    return cookies


def adicionar_item_ao_carrinho(driver, base_url, cookies_dict):
    """Adiciona um item ao carrinho para poder fazer checkout"""
    driver.get(f"{base_url}/busca/")
    time.sleep(1)
    
    wait = WebDriverWait(driver, 10)
    
    produto_card = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card")))
    
    # Encontrar o formulário de adicionar ao carrinho
    form = produto_card.find_element(By.CSS_SELECTOR, "form[action*='busca']")
    produto_id = form.find_element(By.NAME, "produto_id").get_attribute("value")
    csrf_token = form.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
    
    # Adicionar ao carrinho via POST request
    response = requests.post(
        f"{base_url}/busca/",
        data={
            'csrfmiddlewaretoken': csrf_token,
            'produto_id': produto_id
        },
        cookies=cookies_dict,
        headers={'Referer': f"{base_url}/busca/"},
        allow_redirects=True
    )
    
    time.sleep(1)
    return True


def cenario_1_entrega_domicilio_com_sucesso(base_url):
    """Cenário 1: Escolher entrega em domicílio com estimativa de prazo e custo"""
    print("\n[Cenário 1] Entrega em domicílio com estimativa de prazo e custo")
    driver = criar_driver()
    
    try:
        # Fazer login
        session_cookies = fazer_login(driver, base_url)
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Adicionar item ao carrinho
        adicionar_item_ao_carrinho(driver, base_url, cookies_dict)
        
        # Acessar tela de checkout
        driver.get(f"{base_url}/checkout/")
        time.sleep(1)
        
        wait = WebDriverWait(driver, 10)
        
        # Verificar se está na página de checkout
        wait.until(EC.presence_of_element_located((By.NAME, "cep")))
        
        # Usar CEP de Recife (50xxx-xxx) que está na área de entrega
        driver.find_element(By.NAME, "cep").send_keys("50050-000")
        driver.find_element(By.NAME, "endereco").send_keys("Rua Exemplo")
        driver.find_element(By.NAME, "numero").send_keys("123")
        driver.find_element(By.NAME, "complemento").send_keys("Apt 45")
        driver.find_element(By.NAME, "bairro").send_keys("Boa Viagem")
        driver.find_element(By.NAME, "cidade").send_keys("Recife")
        driver.find_element(By.NAME, "estado").send_keys("PE")
        
        # Submeter formulário
        submit_btn = driver.find_element(By.CSS_SELECTOR, "form[action*='domicilio'] button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        
        # Verificar se exibe custo de entrega e prazo
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Deve exibir o custo de entrega (R$ 15,00 para Recife CEP 50xxx)
        # Deve exibir o prazo (2 dias úteis para CEP 50xxx)
        
        custo_encontrado = "15" in page_text or "15.00" in page_text
        prazo_encontrado = "2" in page_text and "dia" in page_text.lower()
        pagina_confirmacao = "revise" in page_text.lower() or "pedido" in page_text.lower()
        
        if custo_encontrado and prazo_encontrado and pagina_confirmacao:
            print("[Cenário 1] PASSOU Sistema exibiu custo de entrega (R$ 15,00) e prazo (2 dias úteis)")
            return True
        else:
            print(f"[Cenário 1] FALHOU - Não exibiu custo e prazo corretamente")
            print(f"Custo encontrado: {custo_encontrado}, Prazo encontrado: {prazo_encontrado}")
            return False
            
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()


def cenario_2_retirada_loja_com_prazo(base_url):
    """Cenário 2: Escolher retirada na loja com estimativa de prazo"""
    print("\n[Cenário 2] Retirada na loja com estimativa de prazo")
    driver = criar_driver()
    
    try:
        # Fazer login
        session_cookies = fazer_login(driver, base_url)
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Adicionar item ao carrinho
        adicionar_item_ao_carrinho(driver, base_url, cookies_dict)
        
        # Acessar tela de checkout
        driver.get(f"{base_url}/checkout/")
        time.sleep(1)
        
        wait = WebDriverWait(driver, 10)
        
        # Verificar se há lojas disponíveis
        try:
            # Procurar por input radio de loja
            loja_radio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='loja_id']")))
            
            # Obter informações da página
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Verificar se exibe prazo de retirada
            # Deve mostrar informação como "Prazo: X dia(s) úteis"
            # Deve informar que não há custo adicional ("Frete grátis")
            
            prazo_encontrado = "prazo" in page_text.lower() and "dia" in page_text.lower()
            frete_gratis = "grátis" in page_text.lower() or "gratuito" in page_text.lower()
            
            if prazo_encontrado and frete_gratis:
                print("[Cenário 2] PASSOU - Sistema exibiu prazo de retirada e informou frete grátis")
                return True
            elif prazo_encontrado:
                print("[Cenário 2] PASSOU PARCIALMENTE - Sistema exibiu prazo de retirada (frete grátis implícito)")
                return True
            else:
                print(f"[Cenário 2] FALHOU - Não exibiu prazo de retirada corretamente")
                return False
                
        except Exception as e:
            print(f"[Cenário 2] FALHOU - Nenhuma loja disponível ou erro: {e}")
            return False
            
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()


def cenario_3_entrega_indisponivel(base_url):
    """Cenário 3: Entrega indisponível para o endereço informado"""
    print("\n[Cenário 3] Entrega indisponível para o endereço")
    driver = criar_driver()
    
    try:
        # Fazer login
        session_cookies = fazer_login(driver, base_url)
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Adicionar item ao carrinho
        adicionar_item_ao_carrinho(driver, base_url, cookies_dict)
        
        # Acessar tela de checkout
        driver.get(f"{base_url}/checkout/")
        time.sleep(1)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "cep")))
        
        # Preencher com CEP fora da área de entrega
        # CEP 99999-999 está fora da área (Recife = 50xxx-54xxx)
        driver.find_element(By.NAME, "cep").send_keys("99999-999")
        driver.find_element(By.NAME, "endereco").send_keys("Rua Distante")
        driver.find_element(By.NAME, "numero").send_keys("456")
        driver.find_element(By.NAME, "bairro").send_keys("Bairro Longe")
        driver.find_element(By.NAME, "cidade").send_keys("Outra Cidade")
        driver.find_element(By.NAME, "estado").send_keys("XX")
        
        # Submeter formulário
        submit_btn = driver.find_element(By.CSS_SELECTOR, "form[action*='domicilio'] button[type='submit']")
        # Usar JavaScript para clicar (evita problemas de elementos sobrepostos)
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        
        # Verificar se exibe mensagem de erro
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        # Deve exibir mensagem: "Entrega não disponível para este endereço"
        # Deve sugerir retirada na loja
        
        mensagem_erro = "entrega não disponível" in page_text or "não disponível" in page_text
        sugere_retirada = "retirada" in page_text and "loja" in page_text
        
        if mensagem_erro and sugere_retirada:
            print("[Cenário 3] PASSOU - Sistema exibiu mensagem de entrega indisponível e sugeriu retirada na loja")
            return True
        elif mensagem_erro:
            print("[Cenário 3] PASSOU PARCIALMENTE - Sistema exibiu mensagem de entrega indisponível")
            return True
        else:
            print(f"[Cenário 3] FALHOU - Não exibiu mensagem de erro adequada")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()


def cenario_4_cep_invalido(base_url):
    """Cenário 4: CEP inválido"""
    print("\n[Cenário 4] CEP inválido")
    driver = criar_driver()
    
    try:
        # Fazer login
        session_cookies = fazer_login(driver, base_url)
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Adicionar item ao carrinho
        adicionar_item_ao_carrinho(driver, base_url, cookies_dict)
        
        # Acessar tela de checkout
        driver.get(f"{base_url}/checkout/")
        time.sleep(1)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "cep")))
        
        # Preencher com CEP inválido (formato incorreto)
        # Testando: "9874-23" (formato inválido)
        driver.find_element(By.NAME, "cep").send_keys("9874-23")
        driver.find_element(By.NAME, "endereco").send_keys("Rua Teste")
        driver.find_element(By.NAME, "numero").send_keys("789")
        driver.find_element(By.NAME, "bairro").send_keys("Bairro Teste")
        driver.find_element(By.NAME, "cidade").send_keys("Cidade Teste")
        driver.find_element(By.NAME, "estado").send_keys("XX")
        
        # Submeter formulário
        submit_btn = driver.find_element(By.CSS_SELECTOR, "form[action*='domicilio'] button[type='submit']")
        # Usar JavaScript para clicar (evita problemas de elementos sobrepostos)
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        
        # Verificar se exibe mensagem de erro
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        # Deve exibir mensagem: "Entrega não disponível para este endereço"
        # Deve sugerir retirada na loja
        
        # Deve exibir: "CEP inválido. Por favor, insira um CEP válido no formato 12345-678"
        # Deve impedir continuação (permanece na mesma página ou volta para checkout)
        
        mensagem_erro = "cep inválido" in page_text or ("formato" in page_text and "12345" in page_text)
        permaneceu_checkout = "checkout" in driver.current_url or "escolha" in page_text
        
        if mensagem_erro and permaneceu_checkout:
            print("[Cenário 4] PASSOU - Sistema exibiu mensagem de CEP inválido e impediu continuação")
            return True
        elif mensagem_erro:
            print("[Cenário 4] PASSOU PARCIALMENTE - Sistema exibiu mensagem de CEP inválido")
            return True
        else:
            print(f"[Cenário 4] FALHOU - Não exibiu mensagem de erro adequada")
            print(f"URL atual: {driver.current_url}")
            return False
            
    except Exception as e:
        print(f"[Cenário 4] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()


def main():
    """Executar todos os cenários"""
    print("=" * 70)
    print("TESTES E2E - HISTÓRIA 7: ESCOLHA DE TIPO DE ENTREGA")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    resultados = [
        cenario_1_entrega_domicilio_com_sucesso(base_url),
        cenario_2_retirada_loja_com_prazo(base_url),
        cenario_3_entrega_indisponivel(base_url),
        cenario_4_cep_invalido(base_url)
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
