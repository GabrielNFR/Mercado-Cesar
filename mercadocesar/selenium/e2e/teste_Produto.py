"""
Testes E2E para História 2: Cadastro de Produtos
Cenários:
1. Cadastrar produto com todos os campos obrigatórios
2. Tentativa de cadastro com campos ausentes
3. Tentativa de cadastro com valores inválidos
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def fazer_login(driver, base_url):
    """Fazer login no sistema"""
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
    
    # Salvar cookies de sessão após login 
    cookies = driver.get_cookies()
    return cookies


def cenario_1_cadastro_completo():
    """Cenário 1: Cadastrar produto com todos os campos obrigatórios"""
    print("\n[Cenário 1] Cadastro com todos os campos obrigatórios")
    driver = criar_driver()
    base_url = "http://localhost:8000"
    
    try:
        session_cookies = fazer_login(driver, base_url)
        
        # Acessar formulário de cadastro
        driver.get(f"{base_url}/produtos/?action=add")
        
        # Aguardar página de formulário carregar
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "codigo")))
        time.sleep(1)
        
        # Obter CSRF token
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        
        # Coletar cookies
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Dados do formulário
        timestamp = str(int(time.time() * 1000))
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'codigo': f'PROD123{timestamp}',
            'nome': f'Arroz {timestamp}',
            'descricao': f'Arroz Integral 5kg {timestamp}',
            'categoria': 'Comida',
            'unidade_medida': 'kg',
            'preco_custo': '10.50',
            'preco': '18.70'
        }
        
        # Fazer POST request via requests library
        response = requests.post(
            f"{base_url}/produtos/?action=add",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/produtos/?action=add"},
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
        
        # Verificar se voltou para listagem 
        if "action=add" not in driver.current_url and "produtos" in driver.current_url:
            print("[Cenário 1] PASSOU - Produto cadastrado com sucesso")
            return True
        else:
            print(f"[Cenário 1] FALHOU - URL: {driver.current_url}, Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_2_campos_ausentes():
    """Cenário 2: Tentativa de cadastro com campos obrigatórios ausentes"""
    print("\n[Cenário 2] Cadastro com campos ausentes")
    driver = criar_driver()
    base_url = "http://localhost:8000"
    
    try:
        session_cookies = fazer_login(driver, base_url)
        
        # Acessar formulário de cadastro
        driver.get(f"{base_url}/produtos/?action=add")
        
        # Aguardar página de formulário carregar
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "codigo")))
        time.sleep(1)
        
        # Obter CSRF token
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Dados do formulário SEM o campo obrigatório preco
        timestamp = str(int(time.time() * 1000))
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'codigo': f'PROD{timestamp}',
            'nome': f'Feijão {timestamp}',
            'descricao': f'Feijão Preto {timestamp}',
            'categoria': 'Alimentos',
            'unidade_medida': 'kg',
            'preco_custo': '8.50'
            # preco NÃO enviado (campo obrigatório)
        }
        
        # Fazer POST via requests
        response = requests.post(
            f"{base_url}/produtos/?action=add",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/produtos/?action=add"},
            allow_redirects=False
        )
        
        # Status 200 indica que permaneceu na página (validação falhou corretamente)
        if response.status_code == 200:
            print("[Cenário 2] PASSOU - Validação bloqueou cadastro")
            return True
        else:
            print(f"[Cenário 2] FALHOU - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_3_valores_invalidos():
    """Cenário 3: Tentativa de cadastro com valores inválidos"""
    print("\n[Cenário 3] Cadastro com valores inválidos")
    driver = criar_driver()
    base_url = "http://localhost:8000"
    
    try:
        session_cookies = fazer_login(driver, base_url)
        
        # Acessar formulário de cadastro
        driver.get(f"{base_url}/produtos/?action=add")
        
        # Aguardar página de formulário carregar
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "codigo")))
        time.sleep(1)
        
        # Obter CSRF token
        csrf_token = driver.find_element(By.NAME, "csrfmiddlewaretoken").get_attribute("value")
        cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        # Dados do formulário com valores NEGATIVOS (inválidos)
        timestamp = str(int(time.time() * 1000))
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'codigo': f'PROD{timestamp}',
            'nome': f'Macarrão {timestamp}',
            'descricao': f'Macarrão {timestamp}',
            'categoria': 'Alimentos',
            'unidade_medida': 'kg',
            'preco_custo': '-10.50',  # Valor negativo (inválido)
            'preco': '-5.90'  # Valor negativo (inválido)
        }
        
        # Fazer POST via requests
        response = requests.post(
            f"{base_url}/produtos/?action=add",
            data=form_data,
            cookies=cookies_dict,
            headers={'Referer': f"{base_url}/produtos/?action=add"},
            allow_redirects=False
        )
        
        # Status 200 indica que permaneceu na página (validação falhou corretamente)
        if response.status_code == 200:
            print("[Cenário 3] PASSOU - Validação bloqueou cadastro")
            return True
        else:
            print(f"[Cenário 3] FALHOU - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def main():
    """Executar todos os cenários"""
    print("=" * 60)
    print("TESTES E2E - HISTÓRIA 2: CADASTRO DE PRODUTOS")
    print("=" * 60)
    
    resultados = [
        cenario_1_cadastro_completo(),
        cenario_2_campos_ausentes(),
        cenario_3_valores_invalidos()
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
