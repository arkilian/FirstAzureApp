# Guia de Implementação - Primeira Azure App

## 🎯 O que foi criado

Esta implementação inclui uma aplicação web completa pronta para ser implantada no Azure:

### Arquitetura da Aplicação

```
FirstAzureApp/
│
├── app.py              # Aplicação Flask principal com API REST
├── requirements.txt    # Dependências Python
├── startup.sh         # Script de inicialização para Azure
├── azure.yaml         # Configuração de deployment Azure
├── .env.example       # Template de variáveis de ambiente
├── README.md          # Documentação completa
│
└── templates/
    └── index.html     # Interface web responsiva em Português
```

### Funcionalidades Implementadas

1. **API REST com Flask**
   - `GET /` - Página principal com interface interativa
   - `GET /health` - Endpoint de health check
   - `GET /init-db` - Inicialização da base de dados
   - `GET /users` - Listagem de utilizadores

2. **Integração PostgreSQL**
   - Conexão segura via psycopg2
   - Gestão de conexões
   - Queries SQL parametrizadas
   - Tratamento de erros

3. **Interface Web**
   - Design responsivo moderno
   - Suporte a português
   - Interação AJAX com a API
   - Feedback visual de operações

4. **Segurança**
   - Debug mode desabilitado em produção
   - Sem exposição de stack traces
   - Dependências atualizadas e sem vulnerabilidades
   - Variáveis de ambiente para configurações sensíveis

## 🚀 Próximos Passos

### 1. Testar Localmente (Sem PostgreSQL)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação (sem BD funcionará parcialmente)
python app.py
```

### 2. Testar Localmente (Com PostgreSQL)

```bash
# Instalar PostgreSQL
# Ubuntu/Debian: sudo apt install postgresql
# MacOS: brew install postgresql

# Criar base de dados
createdb firstazureapp

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# Executar aplicação
python app.py

# Aceder: http://localhost:8000
```

### 3. Deploy na Azure

#### Via Azure CLI:

```bash
# Login
az login

# Criar recursos
az group create --name FirstAzureAppRG --location westeurope

# PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group FirstAzureAppRG \
  --name firstazureapp-db \
  --location westeurope \
  --admin-user azureuser \
  --admin-password <SUA-SENHA-SEGURA> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

# Criar base de dados
az postgres flexible-server db create \
  --resource-group FirstAzureAppRG \
  --server-name firstazureapp-db \
  --database-name firstazureapp

# Deploy da aplicação
az webapp up \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --runtime "PYTHON:3.11" \
  --sku B1

# Configurar variáveis de ambiente
az webapp config appsettings set \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --settings DATABASE_URL="postgresql://azureuser:<SENHA>@firstazureapp-db.postgres.database.azure.com:5432/firstazureapp"
```

#### Via Portal Azure:

1. Aceder ao [Portal Azure](https://portal.azure.com)
2. Criar App Service (Python 3.11)
3. Criar PostgreSQL Flexible Server
4. Configurar variáveis de ambiente no App Service
5. Deploy via Git, GitHub Actions, ou VS Code

### 4. Inicializar Base de Dados

Após o deploy, aceda:
```
https://seu-app.azurewebsites.net/init-db
```

Isso criará a tabela `users` e inserirá dados de exemplo.

### 5. Testar a Aplicação

1. Abra: `https://seu-app.azurewebsites.net`
2. Clique em "Verificar Saúde" - deve mostrar status "healthy"
3. Clique em "Inicializar BD" - cria tabelas e dados
4. Clique em "Listar Utilizadores" - mostra dados da BD

## 🛠️ Personalização

### Adicionar Novos Endpoints

Edite `app.py`:

```python
@app.route('/api/novo-endpoint')
def novo_endpoint():
    return jsonify({
        'mensagem': 'Seu novo endpoint!',
        'dados': []
    })
```

### Adicionar Novas Tabelas

Edite a função `init_db()` em `app.py`:

```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS nova_tabela (
        id SERIAL PRIMARY KEY,
        campo VARCHAR(100)
    );
''')
```

### Modificar Interface

Edite `templates/index.html` para personalizar:
- Cores (variáveis CSS)
- Textos
- Funcionalidades
- Layout

## 📊 Monitorização

### No Azure Portal:

1. Métricas da App Service
2. Logs de aplicação
3. Application Insights (opcional)
4. Métricas da PostgreSQL

### Localmente:

```bash
# Ver logs da aplicação
tail -f logs/app.log  # se configurado

# Monitorar conexões PostgreSQL
psql -d firstazureapp -c "SELECT * FROM pg_stat_activity;"
```

## 🔒 Segurança em Produção

1. **Nunca commitar .env** - use sempre Azure Key Vault ou variáveis de ambiente
2. **Firewall PostgreSQL** - permitir apenas Azure App Service
3. **HTTPS** - Azure fornece certificado SSL gratuito
4. **Autenticação** - adicionar autenticação JWT ou OAuth para endpoints sensíveis
5. **Rate Limiting** - implementar para prevenir abusos
6. **SQL Injection** - já protegido com queries parametrizadas

## 📚 Recursos Adicionais

- [Documentação Flask](https://flask.palletsprojects.com/)
- [Documentação psycopg2](https://www.psycopg.org/docs/)
- [Azure App Service Python](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Azure PostgreSQL](https://docs.microsoft.com/azure/postgresql/)

## 💡 Dicas

1. **Custos**: Use tiers gratuitos ou Basic para desenvolvimento
2. **Performance**: Configure connection pooling para PostgreSQL
3. **Escalabilidade**: Use Azure App Service auto-scaling
4. **Backup**: Configure backups automáticos do PostgreSQL
5. **CI/CD**: Configure GitHub Actions para deploy automático

## ❓ Problemas Comuns

### Erro de conexão à BD
- Verificar firewall do PostgreSQL
- Validar string de conexão
- Confirmar que a BD existe

### App não inicia no Azure
- Verificar logs no Portal Azure
- Confirmar startup command
- Validar requirements.txt

### Erros 500
- Verificar variáveis de ambiente
- Validar conexão à BD
- Consultar logs de aplicação

---

✨ **Parabéns!** Você tem agora uma aplicação Azure completa e funcional!
