### Tutorial 1: Criando um ambiente virtual

Este é um guia detalhado para a criação e utilização de um ambiente virtual Python com o uso do `venv`, um recurso integrado ao Python para a criação de ambientes autônomos. Isso é benéfico para administrar as dependências de projetos de maneira autônoma e prevenir conflitos de pacotes entre projetos distintos. 

### Passo 1: Verificar se o Python está instalado
Antes de criar um ambiente virtual, é importante garantir que você tem o Python instalado.

No terminal (ou prompt de comando), execute:

```bash
python --version
```

Se o Python estiver instalado, isso mostrará a versão. Certifique-se de que seja Python 3.x.

### Passo 2: Criar o ambiente virtual
Com o Python instalado, agora você pode criar um ambiente virtual. Use o comando:

```bash
python -m venv nome_do_ambiente
```

Aqui, `nome_do_ambiente` é o nome que você deseja dar ao seu ambiente virtual. Por exemplo, pode ser `meuambiente`.

### Passo 3: Ativar o ambiente virtual
Uma vez criado o ambiente virtual, é necessário ativá-lo. O método de ativação depende do seu sistema operacional:

* **No Windows**:
  ```bash
  nome_do_ambiente\Scripts\activate
  ```

* **No macOS/Linux**:
  ```bash
  source nome_do_ambiente/bin/activate
  ```

Após a ativação, você verá que o nome do ambiente virtual aparecerá antes do prompt do terminal, indicando que ele está ativo, algo como:

```bash
(meuambiente) $
```

### Passo 4: Instalar pacotes no ambiente virtual
Com o ambiente ativado, qualquer pacote Python instalado via `pip` será isolado nesse ambiente virtual. Por exemplo, para instalar o pacote `pandas`, execute:

```bash
pip install pandas
```

### Passo 5: Verificar pacotes instalados
Para ver os pacotes instalados no ambiente virtual, você pode usar:

```bash
pip list
```

### Passo 6: Desativar o ambiente virtual
Quando terminar de trabalhar, você pode desativar o ambiente virtual com o comando:

```bash
deactivate
```

Após desativar, o prompt do terminal voltará ao normal e você estará fora do ambiente virtual.

### Passo 7: Excluir o ambiente virtual
Se não precisar mais do ambiente virtual, basta excluir a pasta do ambiente que você criou (por exemplo, `meuambiente`).

---

# Instalando dependências em outros sistemas

Para facilitar a instalação de dependências em outros sistemas, você pode salvar as bibliotecas instaladas em um arquivo `requirements.txt`:

  ```bash
  pip freeze > requirements.txt
  ```

  Outros usuários podem instalar os mesmos pacotes com:

  ```bash
  pip install -r requirements.txt
  ```


Isso cobre o básico sobre a criação e o uso de ambientes virtuais com `venv`!