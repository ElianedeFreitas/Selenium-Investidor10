# Automação Selenium — Investidor10 (ITSA3 – 1 dia)

Script em Python (Selenium) que acessa o **Investidor10**, abre a página da **ITSA3** e seleciona a aba **“1 dia”** na seção **COTAÇÃO ITSA3**, salvando um print da seção.

## 📦 Requisitos

- **Python 3.8+**
- **Google Chrome** instalado
- **ChromeDriver** compatível com sua versão do Chrome  
  > Dica: verifique a versão do Chrome em `Ajuda > Sobre o Google Chrome` e baixe o ChromeDriver correspondente.
- Pacotes Python:
  ```bash
  pip install selenium


(Opcional) Para não se preocupar com o caminho do ChromeDriver, você pode usar webdriver-manager. Esse projeto usa caminho local por padrão.

📁 Estrutura sugerida
/
├─ investidor10_itsa3_1dia.py
├─ README.md
└─ .gitignore

⚙️ Configuração

No arquivo investidor10_itsa3_1dia.py, ajuste:

CHROMEDRIVER_PATH → caminho completo do seu chromedriver.exe

DOWNLOAD_DIR → pasta onde o screenshot será salvo (padrão: C:\Users\aluno\Downloads\unieuro_downloads)

HEADLESS = False se quiser ver o navegador durante a execução (recomendado na primeira vez)

▶️ Como executar

No Windows (PowerShell ou Prompt de Comando), na pasta do projeto:

python atividade0310.py


Saída esperada:

Um arquivo cotacao_itsa3_1dia.png salvo na pasta definida em DOWNLOAD_DIR.

🧪 Problemas comuns

FileNotFoundError: ChromeDriver não encontrado
Corrija o caminho em CHROMEDRIVER_PATH para onde o chromedriver.exe realmente está.

Versão incompatível entre Chrome e ChromeDriver
Baixe a versão correta do ChromeDriver compatível com seu Chrome.

Botão “1 dia” não é clicado
Rode com HEADLESS = False e verifique se há pop-up de cookies. O script já tenta fechar automaticamente botões como “Aceitar/Concordo/Entendi”.

🔐 Dica de segurança

Não versione senhas, tokens ou dados pessoais. Evite subir arquivos como *.log, *.env e pastas temporárias.

🧾 Licença

Uso educacional/demonstrativo. Ajuste para sua necessidade.
