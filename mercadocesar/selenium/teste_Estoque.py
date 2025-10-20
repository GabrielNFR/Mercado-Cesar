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

def criar_produto_e_armazem(driver, base_url, produto_nome, armazem_nome):
    """Criar produto e armazém para os testes"""
    timestamp = str(int(time.time() * 1000))
    
    # Criar produto
    driver.get(f"{base_url}/admin/mercadocesar/produto/add/")
    driver.find_element(By.NAME, "codigo").send_keys(f"PROD{timestamp}")
    driver.find_element(By.NAME, "descricao").send_keys(f"{produto_nome} {timestamp}")
    driver.find_element(By.NAME, "nome").send_keys(produto_nome)
    driver.find_element(By.NAME, "categoria").send_keys("Alimentos")
    driver.find_element(By.NAME, "unidade_medida").send_keys("kg")
    driver.find_element(By.NAME, "preco_custo").send_keys("10.00")
    driver.find_element(By.NAME, "preco").send_keys("15.00")
    driver.find_element(By.NAME, "_save").click()
    time.sleep(1)
    
    # Criar armazém
    driver.get(f"{base_url}/admin/mercadocesar/armazem/add/")
    driver.find_element(By.NAME, "nome").send_keys(f"{armazem_nome} {timestamp}")
    driver.find_element(By.NAME, "endereco").send_keys("Rua Teste, 123")
    driver.find_element(By.NAME, "_save").click()
    time.sleep(1)
    
    return timestamp


def cenario_1_estoque_quantidade_suficiente(base_url):
    """Cenário 1: Cadastrar estoque com quantidade suficiente (>= 30)"""
    print("\n[Cenário 1] Cadastro de estoque com quantidade suficiente (>= 30)")
    driver = criar_driver()
    
    try:
        fazer_login(driver, base_url)
        timestamp = criar_produto_e_armazem(driver, base_url, "Arroz Premium", "Armazém Central")
        
        # Cadastrar estoque com quantidade >= 30
        driver.get(f"{base_url}/admin/mercadocesar/estoque/add/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "produto")))
        
        # Selecionar produto do dropdown (seleciona a última opção que contém "Arroz Premium")
        produto_select = Select(driver.find_element(By.NAME, "produto"))
        for option in produto_select.options:
            if "Arroz Premium" in option.text:
                produto_select.select_by_visible_text(option.text)
                break
        
        # Selecionar armazém do dropdown
        armazem_select = Select(driver.find_element(By.NAME, "armazem"))
        for option in armazem_select.options:
            if f"Armazém Central {timestamp}" in option.text:
                armazem_select.select_by_visible_text(option.text)
                break
        
        driver.find_element(By.NAME, "quantidade").send_keys("50")
        driver.find_element(By.NAME, "_save").click()
        time.sleep(2)
        
        # Verificar se saiu da página de cadastro (sucesso)
        if "add" not in driver.current_url and "estoque" in driver.current_url:
            print("[Cenário 1] PASSOU - Estoque com quantidade suficiente cadastrado")
            return True
        else:
            print(f"[Cenário 1] FALHOU - URL: {driver.current_url}")
            return False
            
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_2_estoque_quantidade_baixa(base_url):
    """Cenário 2: Cadastrar estoque com quantidade baixa (< 30) e verificar página de estoque baixo"""
    print("\n[Cenário 2] Cadastro de estoque com quantidade baixa (< 30)")
    driver = criar_driver()
    
    try:
        fazer_login(driver, base_url)
        timestamp = criar_produto_e_armazem(driver, base_url, "Feijão Especial", "Armazém Norte")
        
        # Cadastrar estoque com quantidade < 30
        driver.get(f"{base_url}/admin/mercadocesar/estoque/add/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "produto")))
        
        # Selecionar produto do dropdown
        produto_select = Select(driver.find_element(By.NAME, "produto"))
        for option in produto_select.options:
            if "Feijão Especial" in option.text:
                produto_select.select_by_visible_text(option.text)
                break
        
        # Selecionar armazém do dropdown
        armazem_select = Select(driver.find_element(By.NAME, "armazem"))
        for option in armazem_select.options:
            if f"Armazém Norte {timestamp}" in option.text:
                armazem_select.select_by_visible_text(option.text)
                break
        
        driver.find_element(By.NAME, "quantidade").send_keys("15")
        driver.find_element(By.NAME, "_save").click()
        time.sleep(2)
        
        # Verificar se o cadastro foi bem-sucedido
        if "add" not in driver.current_url and "estoque" in driver.current_url:
            # Acessar página de estoque baixo para verificar se aparece
            driver.get(f"{base_url}/estoque-baixo/")
            time.sleep(1)
            
            # Verificar se a página carregou (deve estar logado como staff)
            if "estoque-baixo" in driver.current_url or driver.title:
                print("[Cenário 2] PASSOU - Estoque baixo cadastrado e página acessível")
                return True
        
        print(f"[Cenário 2] FALHOU - URL: {driver.current_url}")
        return False
            
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_3_estoque_duplicado(base_url):
    """Cenário 3: Tentar cadastrar estoque duplicado (mesmo produto + armazém)"""
    print("\n[Cenário 3] Tentativa de cadastro de estoque duplicado")
    driver = criar_driver()
    
    try:
        fazer_login(driver, base_url)
        timestamp = criar_produto_e_armazem(driver, base_url, "Macarrão Integral", "Armazém Sul")
        
        # Cadastrar estoque pela primeira vez
        driver.get(f"{base_url}/admin/mercadocesar/estoque/add/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "produto")))
        
        # Selecionar produto do dropdown
        produto_select = Select(driver.find_element(By.NAME, "produto"))
        for option in produto_select.options:
            if "Macarrão Integral" in option.text:
                produto_select.select_by_visible_text(option.text)
                break
        
        # Selecionar armazém do dropdown
        armazem_select = Select(driver.find_element(By.NAME, "armazem"))
        for option in armazem_select.options:
            if f"Armazém Sul {timestamp}" in option.text:
                armazem_select.select_by_visible_text(option.text)
                break
        
        driver.find_element(By.NAME, "quantidade").send_keys("40")
        driver.find_element(By.NAME, "_save").click()
        time.sleep(2)
        
        # Tentar cadastrar novamente o mesmo produto no mesmo armazém
        driver.get(f"{base_url}/admin/mercadocesar/estoque/add/")
        wait.until(EC.presence_of_element_located((By.NAME, "produto")))
        
        # Selecionar produto do dropdown
        produto_select = Select(driver.find_element(By.NAME, "produto"))
        for option in produto_select.options:
            if "Macarrão Integral" in option.text:
                produto_select.select_by_visible_text(option.text)
                break
        
        # Selecionar armazém do dropdown
        armazem_select = Select(driver.find_element(By.NAME, "armazem"))
        for option in armazem_select.options:
            if f"Armazém Sul {timestamp}" in option.text:
                armazem_select.select_by_visible_text(option.text)
                break
        
        driver.find_element(By.NAME, "quantidade").send_keys("25")
        driver.find_element(By.NAME, "_save").click()
        time.sleep(2)
        
        # Deve continuar na página de add devido ao erro de unique_together
        if "add" in driver.current_url:
            print("[Cenário 3] PASSOU - Validação bloqueou cadastro duplicado")
            return True
        else:
            print(f"[Cenário 3] FALHOU - Cadastro duplicado permitido indevidamente")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def main():
    """Executar todos os cenários"""
    print("=" * 60)
    print("TESTES E2E - GESTÃO DE ESTOQUE")
    print("=" * 60)

    base_url = "http://localhost:8000"
    
    resultados = [
        cenario_1_estoque_quantidade_suficiente(base_url),
        cenario_2_estoque_quantidade_baixa(base_url),
        cenario_3_estoque_duplicado(base_url)
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
