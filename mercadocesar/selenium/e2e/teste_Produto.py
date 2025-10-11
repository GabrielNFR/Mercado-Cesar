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
    driver.get(f"{base_url}/admin/login/")
    wait = WebDriverWait(driver, 10)
    
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    
    wait.until(EC.url_contains("/admin/"))


def cenario_1_cadastro_completo():
    """Cenário 1: Cadastrar produto com todos os campos obrigatórios"""
    print("\n[Cenário 1] Cadastro com todos os campos obrigatórios")
    driver = criar_driver()
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/admin/mercadocesar/produto/add/")
        
        timestamp = str(int(time.time() * 1000))
        driver.find_element(By.NAME, "codigo").send_keys(f"PROD123{timestamp}")
        driver.find_element(By.NAME, "descricao").send_keys(f"Arroz Integral 5kg {timestamp}")
        driver.find_element(By.NAME, "categoria").send_keys("Comida")
        driver.find_element(By.NAME, "unidade_medida").send_keys("kg")
        driver.find_element(By.NAME, "preco_custo").send_keys("10.50")
        driver.find_element(By.NAME, "preco_venda").send_keys("18.70")
        driver.find_element(By.NAME, "_save").click()
        
        time.sleep(2)
        
        if "add" not in driver.current_url and "produto" in driver.current_url:
            print("[Cenário 1] PASSOU - Produto cadastrado com sucesso")
            return True
        else:
            print(f"[Cenário 1] FALHOU - URL: {driver.current_url}")
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
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/admin/mercadocesar/produto/add/")
        
        timestamp = str(int(time.time() * 1000))
        driver.find_element(By.NAME, "codigo").send_keys(f"PROD{timestamp}")
        driver.find_element(By.NAME, "descricao").send_keys(f"Feijão Preto {timestamp}")
        driver.find_element(By.NAME, "categoria").send_keys("Alimentos")
        driver.find_element(By.NAME, "unidade_medida").send_keys("kg")
        driver.find_element(By.NAME, "preco_custo").send_keys("8.50")
        
        driver.find_element(By.NAME, "_save").click()
        time.sleep(2)
        
        if "add" in driver.current_url:
            print("[Cenário 2] PASSOU - Validação bloqueou cadastro")
            return True
        else:
            print(f"[Cenário 2] FALHOU - URL: {driver.current_url}")
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
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/admin/mercadocesar/produto/add/")
        
        timestamp = str(int(time.time() * 1000))
        driver.find_element(By.NAME, "codigo").send_keys(f"PROD{timestamp}")
        driver.find_element(By.NAME, "descricao").send_keys(f"Macarrão {timestamp}")
        driver.find_element(By.NAME, "categoria").send_keys("Alimentos")
        driver.find_element(By.NAME, "unidade_medida").send_keys("kg")
        driver.find_element(By.NAME, "preco_custo").send_keys("-10.50")
        driver.find_element(By.NAME, "preco_venda").send_keys("-5.90")
        driver.find_element(By.NAME, "_save").click()
        
        time.sleep(2)
        
        if "add" in driver.current_url:
            print("[Cenário 3] PASSOU - Validação bloqueou cadastro")
            return True
        else:
            print(f"[Cenário 3] FALHOU - URL: {driver.current_url}")
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
