"""
Testes E2E para História 3: Cadastro de Cartão de Crédito
Cenários:
1. Cadastro de cartão de crédito com sucesso
2. Tentativa de cadastro com dados inválidos
3. Cadastro de cartão já existente
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
    
    # Salvar cookies de sessão após login bem-sucedido
    cookies = driver.get_cookies()
    return cookies


def cenario_1_cadastro_com_sucesso(base_url):
    """Cenário 1: Cadastro de cartão de crédito com sucesso"""
    print("\n[Cenário 1] Cadastro de cartão com sucesso")
    driver = criar_driver()
    
    try:
        # Fazer login e salvar cookies
        session_cookies = fazer_login(driver, base_url)
        
        # Coletar cookies
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # PASSO 1: Verificar se o cartão já existe e deletá-lo
        driver.get(f"{base_url}/cartoes/")
        time.sleep(1)
        
        # Buscar form de deletar para o cartão com últimos 4 dígitos 0366 (do número 4532015112830366)
        deletar_forms = driver.find_elements(By.CSS_SELECTOR, "form[action*='/cartoes/deletar/']")
        
        for form in deletar_forms:
            # Verificar se é o cartão de teste (procurar por 0366 no card-item pai)
            try:
                cartao_item = form.find_element(By.XPATH, "./ancestor::div[@class='cartao-item']")
                if "0366" in cartao_item.text:
                    form_action = form.get_attribute('action')
                    cartao_id = form_action.split('/deletar/')[-1].rstrip('/')
                    csrf_token_delete = form.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
                    
                    delete_response = requests.post(
                        f"{base_url}/cartoes/deletar/{cartao_id}/",
                        data={'csrfmiddlewaretoken': csrf_token_delete},
                        cookies=cookies_dict,
                        headers={'Referer': f"{base_url}/cartoes/"},
                        allow_redirects=False
                    )
                    
                    time.sleep(1)
                    break
            except:
                pass
        
        # PASSO 2: Acessar cadastro
        wait = WebDriverWait(driver, 10)
        link_cadastrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cadastrar Cartão")))
        link_cadastrar.click()
        time.sleep(2)
        
        wait.until(EC.presence_of_element_located((By.NAME, "numero_cartao")))
        
        # Restaurar cookies de sessão antes de preencher o formulário
        for cookie in session_cookies:
            if cookie['name'] == 'sessionid':
                driver.add_cookie(cookie)
        
        # Preencher dados válidos do cartão
        # Usando número de teste Visa válido (algoritmo de Luhn)
        driver.find_element(By.NAME, "numero_cartao").send_keys("4532015112830366")
        driver.find_element(By.NAME, "validade").send_keys("12/28")
        driver.find_element(By.NAME, "cvv").send_keys("123")
        driver.find_element(By.NAME, "nome_titular").send_keys("João da Silva")
        driver.find_element(By.NAME, "apelido").send_keys("Cartão Principal")
        
        # Verificar se o token CSRF está presente no formulário
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        
        # Atualizar cookies
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Dados do formulário
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'numero_cartao': '4532015112830366',
            'validade': '12/28',
            'cvv': '123',
            'nome_titular': 'João da Silva',
            'apelido': 'Cartão Principal'
        }
        
        # Fazer POST request via requests library
        response = requests.post(
            f"{base_url}/cadastrar/",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/cadastrar/"},
            allow_redirects=False
        )
        
        # Navegar para a URL de redirecionamento
        if response.status_code in (301, 302, 303):
            redirect_url = response.headers.get('Location')
            if redirect_url:
                if not redirect_url.startswith('http'):
                    redirect_url = base_url + redirect_url
                driver.get(redirect_url)
                time.sleep(1)
        
        # Verificar se redirecionou para listagem e se há mensagem de sucesso
        if "listar_cartoes" in driver.current_url or "cartoes" in driver.current_url:
            
            # Buscar o ID do cartão recém-criado na página de listagem e deletá-lo
            try:
                driver.get(f"{base_url}/cartoes/")
                time.sleep(1)
                
                deletar_forms = driver.find_elements(By.CSS_SELECTOR, "form[action*='/cartoes/deletar/']")
                
                if deletar_forms:
                    form_action = deletar_forms[0].get_attribute('action')
                    cartao_id = form_action.split('/deletar/')[-1].rstrip('/')
                    csrf_token_delete = deletar_forms[0].find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
                    
                    delete_response = requests.post(
                        f"{base_url}/cartoes/deletar/{cartao_id}/",
                        data={'csrfmiddlewaretoken': csrf_token_delete},
                        cookies=cookies_dict,
                        headers={'Referer': f"{base_url}/cartoes/"},
                        allow_redirects=False
                    )
                    
            except Exception as e:
                print(f"[Cenário 1] Aviso - Erro ao deletar cartão: {e}")
            
            print("[Cenário 1] PASSOU - Cartão cadastrado com sucesso")
            return True
        else:
            print(f"[Cenário 1] FALHOU - URL atual: {driver.current_url}")
            return False
            
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_2_dados_invalidos(base_url):
    """Cenário 2: Tentativa de cadastro com dados inválidos"""
    print("\n[Cenário 2] Tentativa de cadastro com dados inválidos")
    driver = criar_driver()
    
    try:
        session_cookies = fazer_login(driver, base_url)
        
        # Acessar cadastro clicando no link de navegação
        wait = WebDriverWait(driver, 10)
        link_cadastrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cadastrar Cartão")))
        link_cadastrar.click()
        time.sleep(2)
        
        wait.until(EC.presence_of_element_located((By.NAME, "numero_cartao")))
        
        # Preencher com número de cartão inválido (não passa no algoritmo de Luhn)
        numero_invalido = "1234567890123456"
        driver.find_element(By.NAME, "numero_cartao").send_keys(numero_invalido)
        driver.find_element(By.NAME, "validade").send_keys("12/28")
        driver.find_element(By.NAME, "cvv").send_keys("123")
        driver.find_element(By.NAME, "nome_titular").send_keys("Maria Santos")
        
        # Obter CSRF token
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Fazer POST via requests
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'numero_cartao': numero_invalido,
            'validade': '12/28',
            'cvv': '123',
            'nome_titular': 'Maria Santos',
            'apelido': ''
        }
        
        response = requests.post(
            f"{base_url}/cadastrar/",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/cadastrar/"},
            allow_redirects=False
        )
        
        # Status 200 indica que permaneceu na página (validação falhou corretamente)
        if response.status_code == 200:
            print("[Cenário 2] PASSOU - Sistema rejeitou dados inválidos")
            return True
        else:
            print(f"[Cenário 2] FALHOU - Aceitou dados inválidos")
            return False
            
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_3_cartao_duplicado(base_url):
    """Cenário 3: Cadastro de cartão já existente"""
    print("\n[Cenário 3] Tentativa de cadastro de cartão duplicado")
    driver = criar_driver()
    
    try:
        session_cookies = fazer_login(driver, base_url)
        
        # Coletar cookies
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # PASSO 1: Verificar se o cartão de teste já existe e deletá-lo
        driver.get(f"{base_url}/cartoes/")
        time.sleep(1)
        
        # Buscar form de deletar para o cartão com últimos 4 dígitos 9903 (do número 5425233430109903)
        deletar_forms = driver.find_elements(By.CSS_SELECTOR, "form[action*='/cartoes/deletar/']")
        
        for form in deletar_forms:
            try:
                cartao_item = form.find_element(By.XPATH, "./ancestor::div[@class='cartao-item']")
                if "9903" in cartao_item.text:
                    form_action = form.get_attribute('action')
                    cartao_id = form_action.split('/deletar/')[-1].rstrip('/')
                    csrf_token_delete = form.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
                    
                    delete_response = requests.post(
                        f"{base_url}/cartoes/deletar/{cartao_id}/",
                        data={'csrfmiddlewaretoken': csrf_token_delete},
                        cookies=cookies_dict,
                        headers={'Referer': f"{base_url}/cartoes/"},
                        allow_redirects=False
                    )
                    
                    time.sleep(1)
                    break
            except:
                pass
        
        # PASSO 2: Primeiro cadastro - cadastrar um cartão
        wait = WebDriverWait(driver, 10)
        link_cadastrar = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cadastrar Cartão")))
        link_cadastrar.click()
        time.sleep(2)
        
        wait.until(EC.presence_of_element_located((By.NAME, "numero_cartao")))
        
        # Número de cartão Mastercard válido
        numero_cartao = "5425233430109903"
        
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Primeiro POST - cadastrar cartão
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'numero_cartao': numero_cartao,
            'validade': '06/27',
            'cvv': '456',
            'nome_titular': 'Pedro Oliveira',
            'apelido': ''
        }
        
        response1 = requests.post(
            f"{base_url}/cadastrar/",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/cadastrar/"},
            allow_redirects=False
        )
        
        # Verificar se primeiro cadastro foi bem-sucedido (302)
        if response1.status_code != 302:
            print(f"[Cenário 3] FALHOU - Primeiro cadastro falhou")
            return False
        
        # Navegar para página de cadastro novamente
        driver.get(f"{base_url}/cadastrar/")
        time.sleep(1)
        
        # Segundo POST - tentar cadastrar o mesmo cartão
        csrf_token2 = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        form_data['csrfmiddlewaretoken'] = csrf_token2
        
        response2 = requests.post(
            f"{base_url}/cadastrar/",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/cadastrar/"},
            allow_redirects=False
        )
        
        # Status 200 indica que permaneceu na página (duplicata detectada)
        if response2.status_code == 200:
            
            # Limpar cartão de teste após conclusão
            try:
                driver.get(f"{base_url}/cartoes/")
                time.sleep(1)
                
                deletar_forms = driver.find_elements(By.CSS_SELECTOR, "form[action*='/cartoes/deletar/']")
                for form in deletar_forms:
                    try:
                        cartao_item = form.find_element(By.XPATH, "./ancestor::div[@class='cartao-item']")
                        if "9903" in cartao_item.text:
                            form_action = form.get_attribute('action')
                            cartao_id = form_action.split('/deletar/')[-1].rstrip('/')
                            csrf_token_delete = form.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
                            
                            delete_response = requests.post(
                                f"{base_url}/cartoes/deletar/{cartao_id}/",
                                data={'csrfmiddlewaretoken': csrf_token_delete},
                                cookies=cookies_dict,
                                headers={'Referer': f"{base_url}/cartoes/"},
                                allow_redirects=False
                            )
                            
                            break
                    except:
                        pass
            except Exception as e:
                print(f"[Cenário 3] Aviso - Erro ao deletar cartão: {e}")
            
            print("[Cenário 3] PASSOU - Sistema impediu cadastro duplicado")
            return True
        else:
            print(f"[Cenário 3] FALHOU - Permitiu cadastro duplicado")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def main():
    """Executar todos os cenários"""
    print("=" * 60)
    print("TESTES E2E - HISTÓRIA 3: CADASTRO DE CARTÃO DE CRÉDITO")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    resultados = [
        cenario_1_cadastro_com_sucesso(base_url),
        cenario_2_dados_invalidos(base_url),
        cenario_3_cartao_duplicado(base_url)
    ]
    
    total = len(resultados)
    passou = sum(resultados)
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Total: {total} | Passou: {passou} | Falhou: {total - passou}")
    print("=" * 60)
    
    return 0 if passou == total else 1


if __name__ == "__main__":
    exit(main())