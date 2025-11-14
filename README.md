# FirstAzureApp 🚀

Aplicação exemplo: Python 3.13 + Flask + PostgreSQL + Azure App Service.

## ✨ Visão Geral

Esta aplicação web demonstra uma configuração mínima porém robusta para executar Flask com PostgreSQL na Azure usando infraestrutura como código (Bicep) e práticas de segurança (variáveis de ambiente, pre-commit, detecção de segredos e codificação UTF-8).

Inclui:

- ✅ API REST com Flask
- ✅ Conexão segura com PostgreSQL (sslmode=require)
- ✅ Interface web única (`templates/index.html`)
- ✅ Endpoints para inicialização e listagem de utilizadores
- ✅ Health check que também valida a base de dados
- ✅ Deploy automatizado via `azd deploy`
- ✅ Verificações locais de segurança (detect-secrets + pre-commit)
- ✅ Codificação consistente UTF-8 sem BOM

## 🧱 Arquitetura & Infra

Infraestrutura provisionada com Bicep (`infra/`):

- `main.bicep` orquestra App Service e App Service Plan
- Módulos em `infra/core/host/` para plano e web app
- `azure.yaml` define ambiente para Azure Developer CLI (azd)

Fluxo de deploy: Código → `azd deploy` → Provisiona recursos + publica container de execução (App Service Python) → Configura App Settings (via script ou portal) → App disponível.

## 🧰 Tecnologias

- **Python 3.13** – linguagem principal
- **Flask** – framework web
- **PostgreSQL** – base de dados
- **psycopg2-binary** – driver PostgreSQL
- **Gunicorn** – servidor WSGI para produção (definido em `startup.sh`)
- **Azure App Service** – hosting gerido
- **Azure Developer CLI (azd)** – provisionamento + deploy
- **Bicep** – IaC
- **pre-commit / detect-secrets** – higiene e segurança

## 📂 Estrutura do Projeto

```
FirstAzureApp/
├─ app.py                 # App Flask (rotas, DB, health)
├─ app_simple.py          # Versão simplificada (exemplo)
├─ requirements.txt       # Dependências Python
├─ startup.sh             # Comando de arranque para App Service (gunicorn)
├─ azure.yaml             # Configuração azd
├─ infra/                 # Bicep IaC
│  ├─ main.bicep
│  ├─ main.parameters.json
│  └─ core/host/*.bicep
├─ templates/
│  └─ index.html          # Interface web
├─ test_db_connection.py  # Diagnóstico completo de DB
├─ test_db_simple.py      # Teste rápido de DB
├─ .env.example           # Exemplo de variáveis
├─ .pre-commit-config.yaml# Hooks (higiene + segredos)
├─ .secrets.baseline      # Baseline detect-secrets
├─ convert-to-utf8.ps1    # Script de normalização UTF-8
└─ IMPLEMENTATION_GUIDE.md# Guia técnico adicional
```

## 💻 Instalação Local

### Pré‑requisitos

- Python 3.13+
- PostgreSQL (local ou remoto)
- Azure CLI (para deploy manual) e/ou Azure Developer CLI (`azd`)
- Git

### Passos

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/arkilian/FirstAzureApp.git
   cd FirstAzureApp
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```

   Edite `.env` (exemplo usando variáveis individuais – preferível):
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=firstazureapp
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   FLASK_DEBUG=true
   ```

   Opcionalmente pode usar `DATABASE_URL` (atenção a caracteres especiais: encode com %). O código privilegia DB_* se presentes.

5. **Crie a base de dados:**
   ```bash
   # No PostgreSQL, execute:
   createdb firstazureapp
   ```

6. **Execute a aplicação:**
   ```bash
   python app.py
   ```

7. **Acesse no navegador:**
   ```
   http://localhost:8000
   ```

## 🚀 Deploy na Azure

### Método recomendado: Azure Developer CLI (azd)

1. Login:
   ```bash
   az login
   ```
2. (Uma vez configurado o ambiente em `azure.yaml`) Deploy completo:
   ```bash
   azd env new dev
   azd deploy
   ```
3. Configure as App Settings (se não automatizado):
   ```bash
   az webapp config appsettings set \
     --resource-group <rg> \
     --name <app-name> \
     --settings DB_HOST=<host> DB_PORT=5432 DB_NAME=<db> DB_USER=<user> DB_PASSWORD=<senha>
   ```
4. Verifique endpoint: abra `https://<app-name>.azurewebsites.net/health`.

### Alternativa: Azure CLI manual

1. **Instale a Azure CLI:**
   ```bash
   # Siga as instruções em: https://docs.microsoft.com/cli/azure/install-azure-cli
   ```

2. **Login na Azure:**
   ```bash
   az login
   ```

3. **Crie um grupo de recursos:**
   ```bash
   az group create --name FirstAzureAppRG --location westeurope
   ```

4. **Crie um servidor PostgreSQL:**
   ```bash
   az postgres flexible-server create \
     --resource-group FirstAzureAppRG \
     --name firstazureapp-db \
     --location westeurope \
     --admin-user azureuser \
     --admin-password <sua-senha-segura> \
     --sku-name Standard_B1ms \
     --tier Burstable \
     --version 14
   ```

5. **Crie uma base de dados:**
   ```bash
   az postgres flexible-server db create \
     --resource-group FirstAzureAppRG \
     --server-name firstazureapp-db \
     --database-name firstazureapp
   ```

6. **Crie o App Service:**
   ```bash
   az webapp up \
     --resource-group FirstAzureAppRG \
     --name firstazureapp \
     --runtime "PYTHON:3.11" \
     --sku B1
   ```

7. **Configure variáveis de ambiente (use DB_* em vez de DATABASE_URL):**
   ```bash
   az webapp config appsettings set \
     --resource-group FirstAzureAppRG \
     --name firstazureapp \
     --settings DB_HOST=firstazureapp-db.postgres.database.azure.com DB_PORT=5432 DB_NAME=firstazureapp DB_USER=azureuser DB_PASSWORD=<senha>
   ```

8. **Configure o comando de startup:**
   ```bash
   az webapp config set \
     --resource-group FirstAzureAppRG \
     --name firstazureapp \
     --startup-file "startup.sh"
   ```

### Opção 2: Visual Studio Code

1. Instale a extensão "Azure App Service"
2. Faça login na sua conta Azure
3. Clique com o botão direito na pasta do projeto
4. Selecione "Deploy to Web App"
5. Siga as instruções do assistente

## 📚 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página inicial |
| GET | `/health` | Verificar estado da aplicação e BD |
| GET | `/init-db` | Inicializar a base de dados com dados de exemplo |
| GET | `/users` | Listar todos os utilizadores |

## 🧪 Testar a Aplicação

1. Acesse a página inicial: `http://localhost:8000` ou `https://seu-app.azurewebsites.net`
2. Clique em "Verificar Saúde" para testar a conexão
3. Clique em "Inicializar BD" para criar a tabela e dados de exemplo
4. Clique em "Listar Utilizadores" para ver os dados

## 🔐 Variáveis de Ambiente

| Variável | Propósito |
|----------|-----------|
| `DB_HOST` | Host do PostgreSQL (FQDN no Azure) |
| `DB_PORT` | Porta (default 5432) |
| `DB_NAME` | Nome da base de dados |
| `DB_USER` | Utilizador |
| `DB_PASSWORD` | Senha (não commitar) |
| `FLASK_DEBUG` | Ativa modo debug local |
| `DATABASE_URL` | Alternativa única (apenas se preferir) |

Se ambos presentes, o código usa as variáveis individuais.

## 🛠 Scripts & Testes

- `test_db_simple.py` – teste rápido de conexão (SELECT version())
- `test_db_connection.py` – diagnóstico detalhado (parsing, listagem de tabelas, masking de credenciais)

Executar:
```bash
python test_db_simple.py
python test_db_connection.py
```

## 🧾 Codificação UTF-8

Implementado para evitar caracteres corrompidos:
- `.editorconfig` + `.gitattributes` forçam UTF-8 LF
- `convert-to-utf8.ps1` normaliza ficheiros
- Removido BOM onde necessário (ex.: `app.py`, `index.html`)

## 🛡 Segurança & Segredos

1. Nunca commitar `.env`
2. `.env.example` contém placeholders seguros
3. Pre-commit configurado em `.pre-commit-config.yaml`
4. Baseline de segredos: `.secrets.baseline`
5. Instalação hooks:
   ```bash
   pip install -r requirements.txt  # garante detect-secrets
   pre-commit install
   pre-commit run --all-files
   ```
6. Para atualizar baseline após mudanças justificadas:
   ```bash
   detect-secrets scan --exclude-files "venv|app_logs|app_logs2" > .secrets.baseline
   git add .secrets.baseline
   ```

## 🧩 Desenvolvimento

### Adicionar novos endpoints

Edite `app.py` e adicione novas rotas:

```python
@app.route('/novo-endpoint')
def novo_endpoint():
    return jsonify({'mensagem': 'Olá!'})
```

### Modificar a base de dados

Edite a função `init_db()` em `app.py` para adicionar novas tabelas ou dados.

## 🧯 Troubleshooting

| Problema | Possível Causa | Solução |
|----------|----------------|---------|
| 500 na página inicial | Encoding incorreto | Executar script `convert-to-utf8.ps1` e confirmar sem BOM |
| Erro SSL DB | sslmode ausente | Confirmar string de conexão (usa `sslmode=require`) |
| 404 `/init-db` | Rota não carregada | Verificar se está na versão atual de `app.py` |
| Detect-secrets falha | Baseline não stageada | `git add .secrets.baseline` |
| Password com `@` no URL | Parsing quebra | Usar variáveis separadas ou URL encode `%40` |
| Latência alta DB | Firewall/região | Ajustar VNET / verificar região e RUs |

## 🔒 Boas Práticas (Resumo)

- Reutilizar único `psycopg2.connect` por operação e fechar cursor/conn
- Usar variáveis separadas em vez de URL sempre que possível
- Prevenir exposição: nunca imprimir senha; script de teste mascara credenciais
- Monitorar logs no App Service (`app_logs/` diretório local para referência)

## 📤 Pós-Deploy (Checklist)

1. Aceder `/health` → `status=healthy` e `database=connected`
2. Executar `/init-db` → Mensagem de sucesso
3. Aceder `/users` → Lista de utilizadores exemplo
4. Verificar Application Settings no portal Azure
5. Guardar screenshot para documentação

## 🤝 Contribuições

Contribuições são bem‑vindas: issues, PRs e melhorias de segurança.

## 📄 Licença

MIT – ver ficheiro LICENSE (adicione se ainda não existir).

## 👤 Autor

Exemplo educativo de integração Azure + Python + PostgreSQL.

## 📞 Suporte

- Abrir issue no GitHub
- Documentação Azure: https://learn.microsoft.com/azure/

---

⭐ Se este projeto foi útil, deixe uma estrela!
