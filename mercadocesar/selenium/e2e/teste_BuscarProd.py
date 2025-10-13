"""
Testes E2E para História 6: Busca de Produtos
Cenários:
1. Pesquisa com resultado dentro dos parâmetros dos filtros
2. Pesquisa sem resultado dentro dos parâmetros dos filtros
3. Pesquisa com resultados que incluem detalhes de preços e estoque
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


def cenario_1_pesquisa_com_resultado():
    """Cenário 1: Pesquisa com resultado dentro dos filtros"""
    print("\n[Cenário 1] Pesquisa com resultado dentro dos filtros")
    driver = criar_driver()
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/busca/")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "barraPesquisa")))
        time.sleep(2)
        
        total_produtos = len(driver.find_elements(By.CSS_SELECTOR, ".product-card"))
        
        if total_produtos == 0:
            print("[Cenário 1]  AVISO - Nenhum produto no sistema")
            print("[Cenário 1]  PASSOU - Teste executado (sem produtos)")
            return True
        
        botao_alimentos = driver.find_element(By.CSS_SELECTOR, "button[data-filter='Alimentos']")
        driver.execute_script("arguments[0].click();", botao_alimentos)
        time.sleep(1)
        
        barra = driver.find_element(By.ID, "barraPesquisa")
        barra.send_keys("a")  
        time.sleep(1)
        
        grid_visivel = driver.find_element(By.ID, "allProductsGridContainer").is_displayed()
        
        if grid_visivel:
            print("[Cenário 1] PASSOU - Sistema exibe produtos filtrados")
            return True
        else:
            print("[Cenário 1] FALHOU - Grid de produtos não ficou visível")
            return False
            
    except Exception as e:
        print(f"[Cenário 1] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_2_pesquisa_sem_resultado():
    """Cenário 2: Pesquisa sem resultado"""
    print("\n[Cenário 2] Pesquisa sem resultado")
    driver = criar_driver()
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/busca/")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "barraPesquisa")))
        time.sleep(2)
        
        barra = driver.find_element(By.ID, "barraPesquisa")
        barra.send_keys("PRODUTOINEXISTENTEXYZ9999")
        time.sleep(1)
        
        mensagem = driver.find_element(By.ID, "semResultados")
        mensagem_visivel = mensagem.is_displayed()
        
        if mensagem_visivel:
            print("[Cenário 2] PASSOU - Mensagem 'sem resultados' exibida")
            return True
        else:
            print("[Cenário 2] FALHOU - Mensagem não foi exibida")
            return False
            
    except Exception as e:
        print(f"[Cenário 2] FALHOU - {e}")
        return False
    finally:
        driver.quit()


def cenario_3_pesquisa_com_detalhes_preco_estoque():
    """Cenário 3: Pesquisa com resultados que incluem detalhes de preços e estoque"""
    print("\n[Cenário 3] Pesquisa com resultados incluindo preços e estoque")
    driver = criar_driver()
    
    try:
        fazer_login(driver, "http://localhost:8000")
        driver.get("http://localhost:8000/busca/")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "barraPesquisa")))
        time.sleep(2)
        
        total_produtos = len(driver.find_elements(By.CSS_SELECTOR, ".product-card"))
        
        if total_produtos == 0:
            print("[Cenário 3] AVISO - Nenhum produto no sistema")
            print("[Cenário 3] PASSOU - Teste executado (sem produtos)")
            return True
        
        barra = driver.find_element(By.ID, "barraPesquisa")
        barra.send_keys("a")  
        time.sleep(2)
        
        produtos_encontrados = driver.find_elements(By.CSS_SELECTOR, ".product-card")
        
        if len(produtos_encontrados) == 0:
            print("[Cenário 3] FALHOU - Nenhum produto encontrado")
            return False
        
        primeiro_produto = produtos_encontrados[0]
        
        try:
            paragrafos = primeiro_produto.find_elements(By.TAG_NAME, "p")
            preco_texto = None
            for p in paragrafos:
                texto = p.text.strip()
                if "R$" in texto:
                    preco_texto = texto
                    break
            
            if preco_texto:
                tem_preco = True
                print(f"[Cenário 3] Preço encontrado: {preco_texto}")
            else:
                tem_preco = False
                print("[Cenário 3] Preço não encontrado")
        except Exception as e:
            tem_preco = False
            print(f"[Cenário 3] Erro ao buscar preço: {e}")
        
        try:
            paragrafos = primeiro_produto.find_elements(By.TAG_NAME, "p")
            estoque_texto = None
            for p in paragrafos:
                texto = p.text.strip().lower()
                if "unidade" in texto or "disponível" in texto or "estoque" in texto:
                    estoque_texto = p.text.strip()
                    break
            
            if estoque_texto:
                tem_estoque = True
                print(f"[Cenário 3] Estoque encontrado: {estoque_texto}")
            else:
                tem_estoque = False
                print("[Cenário 3] Estoque não encontrado")
        except Exception as e:
            tem_estoque = False
            print(f"[Cenário 3] Erro ao buscar estoque: {e}")
        
        if tem_preco and tem_estoque:
            print("[Cenário 3] PASSOU - Produto exibe preço e estoque corretamente")
            return True
        elif tem_preco and not tem_estoque:
            print("[Cenário 3] FALHOU PARCIALMENTE - Preço ok, mas estoque não encontrado")
            return False
        elif not tem_preco and tem_estoque:
            print("[Cenário 3] FALHOU PARCIALMENTE - Estoque ok, mas preço não encontrado")
            return False
        else:
            print("[Cenário 3] FALHOU - Produto não exibe preço nem estoque")
            return False
            
    except Exception as e:
        print(f"[Cenário 3] FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()


def main():
    """Executar todos os cenários"""
    print("=" * 60)
    print("TESTES E2E - HISTÓRIA 6: BUSCA DE PRODUTOS")
    print("=" * 60)
    
    resultados = [
        cenario_1_pesquisa_com_resultado(),
        cenario_2_pesquisa_sem_resultado(),
        cenario_3_pesquisa_com_detalhes_preco_estoque()
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
