# Conciliador de Pix (Praxio Luna x Banco do Brasil)

Aplicação desenvolvida para realizar a conciliação de relatórios de vendas via Pix gerados pelo sistema **Praxio Luna** com os extratos bancários de recebimento Pix do **Banco do Brasil**. O sistema possui uma interface de controle desktop que abre um painel no navegador web (rodando localmente).

---

## 📋 Funcionalidades

* **Cruzamento de Dados:** Lê as planilhas Excel do sistema Praxio Luna e do extrato do Banco do Brasil e busca correspondências entre os lançamentos.
* **Conciliação Manual:** Permite que o usuário vincule manualmente transações Pix que não foram pareadas de forma automática, com filtros por data, hora e valor.
* **Salvamento de Estado (Cache):** O andamento das marcações é salvo localmente no disco do computador. Caso a aba do navegador seja fechada, o progresso pode ser recuperado ao abrir novamente.
* **Exportação de PDF:** Gera um relatório formatado em PDF contendo o resumo dos lançamentos conciliados, validados e pendentes.
* **Interface Mista:** Utiliza uma janela nativa do Windows (via Tkinter) apenas para ligar e desligar o servidor, enquanto a interação com os dados ocorre no navegador.

---

## 🛠️ Bibliotecas Utilizadas

O projeto foi construído em Python 3.12 e utiliza as seguintes bibliotecas:
* **`streamlit`:** Criação da interface web interativa.
* **`pandas`, `openpyxl`, `xlrd`:** Leitura e estruturação de planilhas e extração de dados do Excel (.xls e .xlsx).
* **`fpdf2`:** Montagem e exportação do documento em PDF.
* **`tzdata`, `pytz`:** Tratamento de datas e fusos horários nos registros bancários.
* **`pyinstaller`:** Conversão dos scripts Python em um aplicativo executável (.exe).

---

## ⚙️ Como Configurar a Máquina para Rodar o Código

Este repositório contém apenas os arquivos de código (`app.py` e `executar.py`). Para rodar o sistema a partir do código-fonte em qualquer máquina, siga os passos abaixo:

### 1. Instalação do Python
* Baixe e instale o Python através do site oficial (https://www.python.org/downloads/).
* **Atenção:** Na primeira tela do instalador, é obrigatório marcar a opção **"Add Python to PATH"**.

### 2. Download dos Arquivos
Coloque os arquivos `app.py` e `executar.py` juntos em uma mesma pasta no seu computador.

### 3. Instalação das Dependências
Abra o **Terminal** ou **PowerShell** e execute o comando abaixo para instalar as bibliotecas necessárias:

```bash
pip install streamlit pandas openpyxl xlrd fpdf2 tzdata pytz
```

### 4. Executando o Programa
Na pasta onde estão os arquivos, execute o seguinte comando no Terminal/PowerShell:

```bash
python executar.py
```
Isso abrirá a janela de controle do sistema. Clique em "LIGAR SISTEMA" para que o painel seja aberto no navegador.

---

## 📦 Como Compilar para Executável (.exe)

Caso precise rodar a aplicação em computadores que não possuem o Python instalado, é possível compilar o projeto em um executável autossuficiente.

Com as bibliotecas já instaladas na sua máquina de desenvolvimento, abra o PowerShell na pasta do projeto e utilize o comando abaixo:

```powershell
python -m PyInstaller --noconfirm --windowed --add-data "app.py;." --collect-all streamlit --collect-all fpdf2 --collect-all pandas --collect-all tzdata --copy-metadata streamlit --copy-metadata pandas --copy-metadata tzdata --copy-metadata python-dateutil --copy-metadata pytz --hidden-import openpyxl --hidden-import xlrd --hidden-import fpdf --hidden-import pytz --hidden-import tzdata executar.py
```

O PyInstaller criará uma pasta chamada `dist`. Dentro dela, haverá uma pasta chamada `executar` contendo o arquivo `executar.exe` e todos os arquivos de dependência. Basta copiar essa pasta inteira para os outros computadores.

---

## 🔒 Privacidade de Dados

Todo o processamento ocorre localmente. O sistema lê as planilhas e cruza as informações diretamente na memória do computador do usuário, sem realizar conexões com banco de dados externos ou enviar informações financeiras pela internet.
