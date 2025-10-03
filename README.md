# 🖥️ Automação Selenium - Portal EAD Unieuro

Este projeto em **Python + Selenium** automatiza o acesso ao portal **EAD da Unieuro** para:

- Fazer login automaticamente no Moodle da Unieuro.
- Acessar a disciplina **24 | GPSINN | PROJETO INTEGRADOR DE SISTEMAS COMPUTACIONAIS**.
- Localizar e clicar no arquivo **`globo.pdf`**.
- Baixar o PDF automaticamente para uma pasta configurada no Windows.

---

## 🚀 Funcionalidades
- **Login automático** com usuário/senha pré-configurados.
- **Navegação** até a disciplina pelo texto do curso.
- **Busca de arquivo** pelo nome (`globo.pdf`).
- **Download automático** sem abrir popups.
- Opção de rodar com **interface gráfica** (HEADLESS = False) ou em modo invisível (HEADLESS = True).

---

## 🛠️ Requisitos

### Softwares
- [Python 3.10+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)
- [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) **compatível com a versão do Chrome**

### Bibliotecas Python
Crie um ambiente virtual (opcional, recomendado):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
venv\Scripts\activate.bat     # CMD
Instale as dependências:

powershell
Copiar código
pip install selenium
📂 Estrutura do Projeto
bash
Copiar código
Selinium-main/
│
├── chromedriver/                  # Pasta com o chromedriver.exe
│   └── chromedriver.exe
├── login_unieuro.py               # Script principal de automação
├── README.md                      # Documentação do projeto
└── .gitignore                     # Arquivos ignorados no Git
⚙️ Configuração
Baixar ChromeDriver:

Descubra a versão do seu Chrome em chrome://version.

Baixe o ChromeDriver da mesma versão major (exemplo: Chrome 128 → ChromeDriver 128).

Extraia para:

makefile
Copiar código
C:\Users\aluno\Desktop\Selinium-main\Selinium-main\chromedriver\chromedriver.exe
Configurar login no script:

No arquivo login_unieuro.py, altere:

python
Copiar código
LOGIN = "09416619116"
SENHA = "09416619116"
Configurar pasta de download:

Por padrão, os arquivos serão baixados para:

makefile
Copiar código
C:\Users\aluno\Downloads\unieuro_downloads
Você pode mudar no script editando a constante DOWNLOAD_DIR.

▶️ Como Executar
Ative o ambiente virtual (se estiver usando):

powershell
Copiar código
.\venv\Scripts\Activate.ps1
Execute o script:

powershell
Copiar código
python login_unieuro.py
O navegador abrirá, fará login e baixará o arquivo globo.pdf automaticamente.

📥 Resultado
O PDF será salvo em:

makefile
Copiar código
C:\Users\aluno\Downloads\unieuro_downloads
Você verá no terminal mensagens de status, como:

perl
Copiar código
Login realizado.
Curso aberto (provavelmente).
Cliquei no link do PDF. Aguardando download...
Download concluído em: C:\Users\aluno\Downloads\unieuro_downloads\globo.pdf
📌 Observações Importantes
O script foi desenvolvido para uso pessoal e acadêmico.

Mudanças no layout do Moodle podem exigir ajustes nos seletores do Selenium.

Se houver CAPTCHA ou autenticação extra, o login automático pode falhar.

O Chrome e o ChromeDriver precisam estar na mesma major version (ex.: 128/128).
