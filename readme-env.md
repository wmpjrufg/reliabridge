# Configuração do ambiente com `uv`

Este guia mostra como preparar o ambiente de desenvolvimento do **reliabridge** usando o [`uv`](https://docs.astral.sh/uv/) e o **Python 3.11**.

## 1. Instalar o `uv`

### Linux e macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Depois da instalação, confirme que o comando está disponível:

```bash
uv --version
```

Se o terminal não reconhecer o comando, feche-o e abra-o novamente.

## 2. Entrar na pasta do projeto

No terminal, navegue até a raiz do repositório:

```bash
cd caminho/para/reliabridge
```

## 3. Instalar o Python 3.11

O `uv` pode baixar e gerenciar a versão do Python usada pelo projeto:

```bash
uv python install 3.11
```

## 4. Criar o ambiente virtual

Crie um ambiente chamado `.venv` usando o Python 3.11:

```bash
uv venv --python 3.11 .venv
```

## 5. Ativar o ambiente

### Linux e macOS

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### Windows (Prompt de Comando)

```bat
.venv\Scripts\activate.bat
```

Confirme que o ambiente está usando a versão esperada:

```bash
python --version
```

O resultado deve indicar `Python 3.11.x`.

## 6. Instalar as dependências

Com o ambiente ativado, instale os pacotes listados em `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

## 7. Executar o projeto

Inicie a aplicação Streamlit:

```bash
streamlit run app.py
```

Também é possível executar sem ativar o ambiente manualmente:

```bash
uv run streamlit run app.py
```

## 8. Desativar o ambiente

Quando terminar, execute:

```bash
deactivate
```

## Resumo dos comandos

Para configurar o projeto no Linux ou macOS:

```bash
uv python install 3.11
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run app.py
```
