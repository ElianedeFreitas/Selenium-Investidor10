# investidor10_itsa3_1dia.py
import os, time, shutil, tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# ===== CONFIG =====
URL_HOME = "https://investidor10.com.br/"
TICKER   = "ITSA3"

HEADLESS = False   # use False se o site bloquear headless
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 25
PROFILE_DIR = None

# Caminho do seu ChromeDriver local (com .exe no Windows)
CHROMEDRIVER_PATH = r"C:\Users\aluno\Desktop\Selinium-main\chromedriver\chromedriver.exe"

# Pasta de saída para prints
DOWNLOAD_DIR = r"C:\Users\aluno\Downloads\unieuro_downloads"
SCREENSHOT_NAME = f"cotacao_{TICKER.lower()}_1dia.png"

def create_driver(headless: bool = False):
    """
    Cria o driver Chrome com um perfil temporário e opções que ajudam a automação.
    """
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

    # Preferências (mantidas caso um dia precise baixar algo)
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
    Dentro de 'container' (driver ou WebElement), clica no primeiro elemento
    cliqueável cujo texto visível case-insensitive contenha 'texto'.
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
    """
    Fecha popups de cookies/comunicados comuns (Aceitar/Concordo/Entendi/OK).
    Ignora silenciosamente se não encontrar nada.
    """
    textos = ["Aceitar", "Aceitar todos", "Concordo", "Entendi", "OK", "Fechar", "Continuar", "Prosseguir", "Permitir"]
    for t in textos:
        try:
            clicar_elemento_por_texto(driver, t, timeout=5)
            time.sleep(0.4)
            return True
        except Exception:
            pass
    return False

def abrir_pagina_acao(driver, ticker: str):
    """
    Vai direto na URL da ação (ex.: /acoes/itsa3/). Se falhar, tenta home -> busca/click.
    """
    destino = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
    try:
        driver.get(destino)
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH, f"//h1[contains(., '{ticker.upper()}')] | //h2[contains(., '{ticker.upper()}')]"))
        )
        return True
    except TimeoutException:
        # fallback: home e clique/Busca básica
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

        # último recurso: tenta de novo a URL direta
        driver.get(destino)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//h1[contains(., '{ticker.upper()}')] | //h2[contains(., '{ticker.upper()}')]"))
            )
            return True
        except TimeoutException:
            return False

def encontrar_aba_1_dia(container, timeout=EXPLICIT_WAIT):
    """
    Procura a aba/botão '1 dia' usando vários seletores:
    - Texto visível '1 dia' (com e sem acento)
    - Atributos comuns: data-range='1d', href*='1d'
    - Tags: a, button, li, span, div
    Retorna o WebElement ou lança TimeoutException.
    """
    tentativas = [
        # texto exato/normalizado
        ".//a[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//button[normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",
        ".//*[self::li or self::span or self::div][normalize-space(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'))='1 dia']",

        # contém (para lidar com espaços extras)
        ".//a[contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",
        ".//button[contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",
        ".//*[self::li or self::span or self::div][contains(translate(.,'ÂÃÁÀÉÊÍÓÔÕÚÇ','âãáàéêíóôõúç'),'1 dia')]",

        # atributos/links típicos
        ".//*[@data-range='1d']",
        ".//a[contains(@href, '1d')]",
        ".//li[contains(@class,'active')]/a[contains(@href,'1d')]",
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
        time.sleep(0.25)

    raise TimeoutException(f"Não localizei a aba '1 dia'. Último erro: {last_err}")

def mostrar_aba_1_dia_e_print(driver, ticker: str, out_path: str):
    """
    Localiza a seção 'COTAÇÃO <ticker>', clica de forma robusta na aba '1 dia'
    (JS click + retry), valida que ficou ativa e salva o screenshot da seção.
    """
    wait = WebDriverWait(driver, EXPLICIT_WAIT)

    # Fecha pop-ups se houver
    tentar_fechar_cookies(driver)

    # Seção da cotação do ticker (h2 contém 'COTAÇÃO ITSA3')
    sec = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//h2[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÉÊÍÓÔÕÚÇ','abcdefghijklmnopqrstuvwxyzáâãàéêíóôõúç'), 'cotação {ticker.lower()}')]/ancestor::*[self::section or self::div][1]")
    ))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sec)
    time.sleep(0.5)

    # Às vezes um header fixo cobre os tabs; sobe um pouco a página
    driver.execute_script("window.scrollBy(0, -120);")

    # Encontra a aba '1 dia'
    try:
        aba = encontrar_aba_1_dia(sec, timeout=10)
    except TimeoutException:
        # tenta globalmente como fallback
        aba = encontrar_aba_1_dia(driver, timeout=8)

    # Clique robusto: normal; se falhar, usa JS
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
            # último recurso: click() direto de novo
            try:
                aba.click()
            except Exception:
                pass

    # Aguarda estado "ativo" (classe 'active' ou aria-selected="true")
    def aba_ativa():
        try:
            aria = aba.get_attribute("aria-selected")
            if aria and aria.lower() == "true":
                return True
            # classe active no próprio elemento ou no pai LI/A/Button
            try:
                pai = aba.find_element(By.XPATH, "./ancestor-or-self::*[self::li or self::a or self::button][1]")
                classes = " ".join(filter(None, [aba.get_attribute("class") or "", pai.get_attribute("class") or ""]))
            except NoSuchElementException:
                classes = aba.get_attribute("class") or ""
            if "active" in classes:
                return True
        except Exception:
            pass
        return False

    t0 = time.time()
    while time.time() - t0 < 6:
        if aba_ativa():
            break
        time.sleep(0.25)

    # pequena espera para o gráfico/tabela atualizar
    time.sleep(1.0)

    # Screenshot da seção
    out_full = os.path.join(DOWNLOAD_DIR, out_path)
    try:
        sec.screenshot(out_full)
        print(f"[OK] Screenshot (1 dia) salvo em: {out_full}")
    except WebDriverException:
        driver.save_screenshot(out_full)
        print(f"[WARN] Screenshot do elemento falhou; salvei a janela inteira: {out_full}")

def main():
    driver = None
    try:
        driver = create_driver(HEADLESS)
        ok = abrir_pagina_acao(driver, TICKER)
        if not ok:
            print("Não consegui abrir a página da ação.")
            return

        mostrar_aba_1_dia_e_print(driver, TICKER, SCREENSHOT_NAME)

        if not HEADLESS:
            print("Deixando o navegador aberto por 6s para inspeção…")
            time.sleep(6)

    finally:
        if driver:
            driver.quit()
        global PROFILE_DIR
        if PROFILE_DIR and os.path.isdir(PROFILE_DIR):
            shutil.rmtree(PROFILE_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
