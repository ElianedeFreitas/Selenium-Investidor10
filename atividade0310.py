# investidor10_cotacao_1dia.py
import os, time, shutil, tempfile, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# ===== CONFIG =====
URL_HOME = "https://investidor10.com.br/"
TICKER   = "ITSA3"   # Troque aqui para testar outras ações (ex.: "PETR4", "VALE3")

HEADLESS = False     # use False se o site bloquear headless
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 25
PROFILE_DIR = None

# Caminho do seu ChromeDriver local (com .exe no Windows)
CHROMEDRIVER_PATH = r"C:\Users\aluno\Desktop\Selinium-main\chromedriver\chromedriver.exe"

# Pasta de saída para prints
DOWNLOAD_DIR = r"C:\Users\aluno\Downloads\unieuro_downloads"
SCREENSHOT_NAME = f"cotacao_{TICKER.lower()}_1dia.png"

# ---------- Utils ----------
def _extrair_numero_brl(texto: str):
    """
    Extrai o primeiro número em formato BR (R$ 13,45 / 13,45 / 1.234,56) -> (float, texto_original)
    (Usado apenas para converter o texto do card em número; a BUSCA é pelo rótulo 'COTAÇÃO', não pelo valor.)
    """
    if not texto:
        return None, None
    m = re.search(r"(R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+,\d+)", texto)
    if not m:
        return None, None
    bruto = m.group(0)
    num = m.group(2) if m.group(2) else bruto
    num_normal = num.replace(".", "").replace(",", ".")
    try:
        return float(num_normal), bruto.strip()
    except ValueError:
        return None, None

# ---------- Selenium setup ----------
def create_driver(headless: bool = False):
    global PROFILE_DIR
    PROFILE_DIR = tempfile.mkdtemp(prefix="selenium_profile_")

    if not os.path.exists(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver não encontrado em: {CHROMEDRIVER_PATH}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def clicar_elemento_por_texto(container, texto, timeout=EXPLICIT_WAIT):
    """
    Clica no primeiro elemento cujo texto contenha 'texto' (case-insensitive).
    """
    xpath = (
        ".//a[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),"
        f"{repr(texto.lower())})] | "
        ".//button[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),"
        f"{repr(texto.lower())})] | "
        ".//*[self::li or self::span or self::div][contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'),"
        f"{repr(texto.lower())})]"
    )
    el = WebDriverWait(container, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    el.click()
    return True

def tentar_fechar_cookies(driver):
    textos = ["Aceitar", "Aceitar todos", "Concordo", "Entendi", "OK", "Fechar", "Continuar", "Prosseguir", "Permitir"]
    for t in textos:
        try:
            clicar_elemento_por_texto(driver, t, timeout=5)
            time.sleep(0.3)
            return True
        except Exception:
            pass
    return False

def abrir_pagina_acao(driver, ticker: str):
    """
    Abre diretamente /acoes/<ticker>/ e verifica o cabeçalho com o ticker.
    """
    destino = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
    try:
        driver.get(destino)
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH, f"//h1[contains(., '{ticker.upper()}')] | //h2[contains(., '{ticker.upper()}')]"))
        )
        return True
    except TimeoutException:
        # Fallback simples
        driver.get(URL_HOME)
        tentar_fechar_cookies(driver)
        try:
            clicar_elemento_por_texto(driver, "Ações", timeout=8)
            time.sleep(0.5)
        except Exception:
            pass
        try:
            clicar_elemento_por_texto(driver, ticker.upper(), timeout=8)
            return True
        except Exception:
            pass
        return False

# ---------- CAPTURAR A COTAÇÃO DO CARD "COTAÇÃO" ----------
def obter_cotacao_atual(driver, ticker: str):
    """
    Captura o número exibido no **card 'COTAÇÃO'** (logo acima do gráfico).
    Não depende do valor; depende do rótulo 'COTAÇÃO'.
    Retorna (valor_float_ou_None, texto_exibido_ou_None).
    """
    wait = WebDriverWait(driver, 10)

    # 1) Localiza o card/bloco cujo rótulo (qualquer subelemento) é exatamente 'COTAÇÃO'
    #    (case-insensitive, com/sem acento). Sobe para o container (div/section) mais próximo.
    try:
        bloco = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[self::div or self::section]"
            "[.//*[self::div or self::span or self::strong or self::h3 or self::h4]"
            "[normalize-space(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'))='cotação']][1]"
        )))
    except TimeoutException:
        return None, None

    # 2) Dentro desse bloco, pegue o texto do preço (procurando elementos usuais)
    candidatos_xp = [
        ".//span[contains(.,'R$')][1]",
        ".//strong[contains(.,'R$')][1]",
        ".//div[contains(.,'R$')][1]",
        ".//p[contains(.,'R$')][1]",
        # Fallback SEM 'R$': primeiro elemento textual que pareça número BR
        ".//span[normalize-space(.)][1]",
        ".//strong[normalize-space(.)][1]",
        ".//div[normalize-space(.)][1]",
        ".//p[normalize-space(.)][1]",
    ]

    texto_encontrado = ""
    for xp in candidatos_xp:
        try:
            el = bloco.find_element(By.XPATH, xp)
            txt = (el.text or "").strip()
            if not txt:
                continue
            if "R$" in txt or re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}", txt):
                texto_encontrado = txt
                break
        except Exception:
            continue

    if not texto_encontrado:
        return None, None

    # 3) Converte para float (apenas para exibir também em formato numérico)
    val, bruto = _extrair_numero_brl(texto_encontrado)
    return val, (bruto or texto_encontrado)

# ---------- Selecionar aba "1 dia" + screenshot ----------
def encontrar_aba_1_dia(container, timeout=EXPLICIT_WAIT):
    tentativas = [
        ".//a[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//button[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//*[self::li or self::span or self::div][normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//a[contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",
        ".//button[contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",
        ".//*[self::li or self::span or self::div][contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",
        ".//*[@data-range='1d']",
        ".//a[contains(@href, '1d')]",
        ".//button[contains(@data-range, '1d')]",
        ".//*[contains(@aria-controls, '1d')]",
        ".//*[contains(@data-tab, '1d')]",
    ]
    fim = time.time() + timeout
    last_err = None
    while time.time() < fim:
        for xp in tentativas:
            try:
                el = container.find_element(By.XPATH, xp)
                return el
            except Exception as e:
                last_err = e
        time.sleep(0.2)
    raise TimeoutException(f"Não localizei a aba '1 dia'. Último erro: {last_err}")

def mostrar_aba_1_dia_e_print(driver, ticker: str, out_path: str):
    wait = WebDriverWait(driver, EXPLICIT_WAIT)
    tentar_fechar_cookies(driver)

    # Seção "COTAÇÃO <ticker>" (título acima do gráfico)
    sec = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//h2[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'), 'cotação {ticker.lower()}')]/ancestor::*[self::section or self::div][1]")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sec)
    time.sleep(0.4)
    driver.execute_script("window.scrollBy(0, -120);")  # evita header fixo cobrindo

    try:
        aba = encontrar_aba_1_dia(sec, timeout=10)
    except TimeoutException:
        aba = encontrar_aba_1_dia(driver, timeout=8)

    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(aba))
        aba.click()
    except Exception:
        try:
            driver.execute_script(
                "arguments[0].dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));",
                aba
            )
        except Exception:
            try:
                aba.click()
            except Exception:
                pass

    # pequena espera para atualização visual do gráfico
    time.sleep(1.0)

    # Screenshot da seção
    out_full = os.path.join(DOWNLOAD_DIR, out_path)
    try:
        sec.screenshot(out_full)
        print(f"[OK] Screenshot (1 dia) salvo em: {out_full}")
    except WebDriverException:
        driver.save_screenshot(out_full)
        print(f"[WARN] Screenshot do elemento falhou; salvei a janela inteira: {out_full}")

# ---------- Main ----------
def main():
    driver = None
    try:
        driver = create_driver(HEADLESS)

        if not abrir_pagina_acao(driver, TICKER):
            print("Não consegui abrir a página da ação.")
            return

        # Lê a COTAÇÃO do card (sem depender do valor em si)
        valor, bruto = obter_cotacao_atual(driver, TICKER)
        if valor is not None:
            print(f"[INFO] COTAÇÃO {TICKER}: {bruto}  (numérico: {valor:.2f})")
        else:
            print(f"[WARN] Não consegui ler a COTAÇÃO de {TICKER} (card 'COTAÇÃO').")

        # Seleciona 1 dia e tira o print
        mostrar_aba_1_dia_e_print(driver, TICKER, SCREENSHOT_NAME)

        if not HEADLESS:
            print("Deixando o navegador aberto por 6s para inspeção…")
            time.sleep(6)

        if valor is not None:
            print(f"\n==== RESUMO ====\nCOTAÇÃO {TICKER} agora: {bruto} (~{valor:.2f})\nScreenshot: {os.path.join(DOWNLOAD_DIR, SCREENSHOT_NAME)}\n")
        else:
            print("\n==== RESUMO ====\nCOTAÇÃO não encontrada. Veja o screenshot e me diga o HTML do card para ajustar o seletor.\n")

    finally:
        if driver:
            driver.quit()
        global PROFILE_DIR
        if PROFILE_DIR and os.path.isdir(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
