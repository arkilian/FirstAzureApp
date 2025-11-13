# Guia de ImplementaÃ§Ã£o - Primeira Azure App

## ðŸŽ¯ O que foi criado

Esta implementaÃ§Ã£o inclui uma aplicaÃ§Ã£o web completa pronta para ser implantada no Azure:

### Arquitetura da AplicaÃ§Ã£o

```
FirstAzureApp/
â”‚
â”œâ”€â”€ app.py              # AplicaÃ§Ã£o Flask principal com API REST
â”œâ”€â”€ requirements.txt    # DependÃªncias Python
â”œâ”€â”€ startup.sh         # Script de inicializaÃ§Ã£o para Azure
â”œâ”€â”€ azure.yaml         # ConfiguraÃ§Ã£o de deployment Azure
â”œâ”€â”€ .env.example       # Template de variÃ¡veis de ambiente
â”œâ”€â”€ README.md          # DocumentaÃ§Ã£o completa
â”‚
â””â”€â”€ templates/
    â””â”€â”€ index.html     # Interface web responsiva em PortuguÃªs
```

### Funcionalidades Implementadas

1. **API REST com Flask**
   - `GET /` - PÃ¡gina principal com interface interativa
   - `GET /health` - Endpoint de health check
   - `GET /init-db` - InicializaÃ§Ã£o da base de dados
   - `GET /users` - Listagem de utilizadores

2. **IntegraÃ§Ã£o PostgreSQL**
   - ConexÃ£o segura via psycopg2
   - GestÃ£o de conexÃµes
   - Queries SQL parametrizadas
   - Tratamento de erros

3. **Interface Web**
   - Design responsivo moderno
   - Suporte a portuguÃªs
   - InteraÃ§Ã£o AJAX com a API
   - Feedback visual de operaÃ§Ãµes

4. **SeguranÃ§a**
   - Debug mode desabilitado em produÃ§Ã£o
   - Sem exposiÃ§Ã£o de stack traces
   - DependÃªncias atualizadas e sem vulnerabilidades
   - VariÃ¡veis de ambiente para configuraÃ§Ãµes sensÃ­veis

## ðŸš€ PrÃ³ximos Passos

### 1. Testar Localmente (Sem PostgreSQL)

```bash
# Instalar dependÃªncias
pip install -r requirements.txt

# Executar aplicaÃ§Ã£o (sem BD funcionarÃ¡ parcialmente)
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

# Executar aplicaÃ§Ã£o
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

# Deploy da aplicaÃ§Ã£o
az webapp up \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --runtime "PYTHON:3.11" \
  --sku B1

# Configurar variÃ¡veis de ambiente
az webapp config appsettings set \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --settings DATABASE_URL="postgresql://azureuser:<SENHA>@firstazureapp-db.postgres.database.azure.com:5432/firstazureapp"
```

#### Via Portal Azure:

1. Aceder ao [Portal Azure](https://portal.azure.com)
2. Criar App Service (Python 3.11)
3. Criar PostgreSQL Flexible Server
4. Configurar variÃ¡veis de ambiente no App Service
5. Deploy via Git, GitHub Actions, ou VS Code

### 4. Inicializar Base de Dados

ApÃ³s o deploy, aceda:
```
https://seu-app.azurewebsites.net/init-db
```

Isso criarÃ¡ a tabela `users` e inserirÃ¡ dados de exemplo.

### 5. Testar a AplicaÃ§Ã£o

1. Abra: `https://seu-app.azurewebsites.net`
2. Clique em "Verificar SaÃºde" - deve mostrar status "healthy"
3. Clique em "Inicializar BD" - cria tabelas e dados
4. Clique em "Listar Utilizadores" - mostra dados da BD

## ðŸ› ï¸ PersonalizaÃ§Ã£o

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

Edite a funÃ§Ã£o `init_db()` em `app.py`:

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
- Cores (variÃ¡veis CSS)
- Textos
- Funcionalidades
- Layout

## ðŸ“Š MonitorizaÃ§Ã£o

### No Azure Portal:

1. MÃ©tricas da App Service
2. Logs de aplicaÃ§Ã£o
3. Application Insights (opcional)
4. MÃ©tricas da PostgreSQL

### Localmente:

```bash
# Ver logs da aplicaÃ§Ã£o
tail -f logs/app.log  # se configurado

# Monitorar conexÃµes PostgreSQL
psql -d firstazureapp -c "SELECT * FROM pg_stat_activity;"
```

## ðŸ”’ SeguranÃ§a em ProduÃ§Ã£o

1. **Nunca commitar .env** - use sempre Azure Key Vault ou variÃ¡veis de ambiente
2. **Firewall PostgreSQL** - permitir apenas Azure App Service
3. **HTTPS** - Azure fornece certificado SSL gratuito
4. **AutenticaÃ§Ã£o** - adicionar autenticaÃ§Ã£o JWT ou OAuth para endpoints sensÃ­veis
5. **Rate Limiting** - implementar para prevenir abusos
6. **SQL Injection** - jÃ¡ protegido com queries parametrizadas

## ðŸ“š Recursos Adicionais

- [DocumentaÃ§Ã£o Flask](https://flask.palletsprojects.com/)
- [DocumentaÃ§Ã£o psycopg2](https://www.psycopg.org/docs/)
- [Azure App Service Python](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Azure PostgreSQL](https://docs.microsoft.com/azure/postgresql/)

## ðŸ’¡ Dicas

1. **Custos**: Use tiers gratuitos ou Basic para desenvolvimento
2. **Performance**: Configure connection pooling para PostgreSQL
3. **Escalabilidade**: Use Azure App Service auto-scaling
4. **Backup**: Configure backups automÃ¡ticos do PostgreSQL
5. **CI/CD**: Configure GitHub Actions para deploy automÃ¡tico

## â“ Problemas Comuns

### Erro de conexÃ£o Ã  BD
- Verificar firewall do PostgreSQL
- Validar string de conexÃ£o
- Confirmar que a BD existe

### App nÃ£o inicia no Azure
- Verificar logs no Portal Azure
- Confirmar startup command
- Validar requirements.txt

### Erros 500
- Verificar variÃ¡veis de ambiente
- Validar conexÃ£o Ã  BD
- Consultar logs de aplicaÃ§Ã£o

---

âœ¨ **ParabÃ©ns!** VocÃª tem agora uma aplicaÃ§Ã£o Azure completa e funcional!
