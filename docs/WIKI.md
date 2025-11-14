# FirstAzureApp Wiki

## 1. Linha do Tempo (Cronologia das Ações)

| Ordem | Etapa | Objetivo | Resultado |
|-------|------|---------|-----------|
| 1 | Criação de `test_db_connection.py` | Validar conectividade PostgreSQL isolada | Conexão estabelecida, versão do servidor exibida |
| 2 | Adição de leitura de `.env` | Externalizar credenciais | Variáveis DB_* carregadas com sucesso |
| 3 | Correção de parsing `DATABASE_URL` com `@` na password | Evitar quebras na URL | Troca para variáveis separadas DB_* recomendada |
| 4 | Integração no `app.py` (rotas /db/test /db/tables) | Tornar teste acessível via API | Flask expõe saúde da BD |
| 5 | Ativação venv e instalação dependências | Ambiente isolado | `psycopg2-binary` funcional em Windows |
| 6 | Deploy inicial Azure App Service | Publicar aplicação | Página /health acessível na nuvem |
| 7 | Remoção de segredos do Bicep | Segurança IaC | `main.bicep` sem credenciais hardcoded |
| 8 | Padronização UTF-8 (headers/.editorconfig/.gitattributes) | Evitar caracteres corrompidos | Arquivos convertidos para UTF-8 sem BOM |
| 9 | Implementação pre-commit + detect-secrets | Prevenir exposição de segredos | Hooks instalados e baseline criada |
| 10 | Correção de baseline (encoding + staging) | Fazer hook passar | `detect-secrets` passa em todos os commits |
| 11 | Criação endpoints `/init-db` e `/users` | Funcionalidade CRUD inicial | BD inicializa com dados de exemplo |
| 12 | Recuperação de encoding corrompido no `index.html` | Corrigir interface | Emojis e acentuação normalizados |
| 13 | Atualização `/health` para verificar DB | Health abrangente | Retorna `database=connected` |
| 14 | Deploy final com `azd deploy` | Publicar versão estável | App funcional com todos endpoints |
| 15 | Atualização README & Wiki | Documentação completa | Onboarding facilitado |

## 2. Infraestrutura (Bicep + azd)

- `infra/main.bicep` orquestra recursos.
- App Settings configuradas fora do ficheiro para evitar segredos.
- Deploy: `azd env new dev && azd deploy`.

## 3. Variáveis de Ambiente

Usadas no código (`get_db_connection()`):
```
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
FLASK_DEBUG (apenas local)
```
Fallback: `DATABASE_URL` (não recomendado se existir password com caracteres especiais sem encoding).

## 4. Testes de Base de Dados

- `test_db_simple.py` – Conexão rápida + versão.
- `test_db_connection.py` – Máscara de credenciais, listagem de tabelas, fallback de URL.

Execução:
```bash
python test_db_simple.py
python test_db_connection.py
```

## 5. Segurança

- `.env` ignorado (não versionar segredos reais)
- `.env.example` pedagogicamente seguro
- `detect-secrets` baseline: `.secrets.baseline`
- Atualizar baseline quando justificável:
```bash
detect-secrets scan --exclude-files "venv|app_logs|app_logs2" > .secrets.baseline
git add .secrets.baseline
```

## 6. Codificação UTF-8

Problema: Acentos e emojis corrompidos (sequências `Ã°Å¸`).
Solução:
- Conversão com `convert-to-utf8.ps1`
- Remoção de BOM em ficheiros críticos
- Adoção de `.editorconfig` e `.gitattributes` para consistência

## 7. Endpoints Principais

| Endpoint | Função |
|----------|--------|
| `/` | Interface HTML |
| `/health` | Estado aplicação + teste DB |
| `/init-db` | Criação da tabela `users` + seed |
| `/users` | Listagem dos utilizadores |
| `/db/test` | Teste direto de conexão |
| `/db/tables` | Inventário de tabelas públicas |

## 8. Comandos Azure CLI Utilizados

### 8.1 Criação de Recursos

#### Login e Configuração Inicial
```bash
# Autenticação no Azure
az login

# Listar subscrições disponíveis
az account list --output table

# Definir subscrição ativa
az account set --subscription "<SUBSCRIPTION_ID>"
```

#### Criação do Resource Group
```bash
# Criar grupo de recursos
az group create \
  --name rg-firstapp-dev \
  --location westeurope
```

#### Criação do PostgreSQL Flexible Server
```bash
# Criar servidor PostgreSQL
az postgres flexible-server create \
  --resource-group rg-firstapp-dev \
  --name postgres-firstapp-dev \
  --location westeurope \
  --admin-user dbadmin \
  --admin-password <SUA-SENHA-SEGURA> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14 \
  --storage-size 32 \
  --public-access 0.0.0.0

# Criar base de dados
az postgres flexible-server db create \
  --resource-group rg-firstapp-dev \
  --server-name postgres-firstapp-dev \
  --database-name firstappdb

# Configurar firewall (permitir serviços Azure)
az postgres flexible-server firewall-rule create \
  --resource-group rg-firstapp-dev \
  --name postgres-firstapp-dev \
  --rule-name AllowAllAzureIPs \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Configurar firewall (seu IP local para testes)
az postgres flexible-server firewall-rule create \
  --resource-group rg-firstapp-dev \
  --name postgres-firstapp-dev \
  --rule-name AllowMyIP \
  --start-ip-address <SEU-IP> \
  --end-ip-address <SEU-IP>
```

#### Criação do App Service (via Azure Developer CLI)
```bash
# Inicializar ambiente azd
azd init

# Criar novo ambiente
azd env new dev

# Provisionar infraestrutura (cria App Service Plan + App Service)
azd provision

# Ou deploy completo (provisiona + publica código)
azd deploy
```

### 8.2 Configuração de Aplicação

#### Configurar App Settings (Variáveis de Ambiente)
```bash
# Obter nome do web app
$webAppName = az webapp list \
  --resource-group rg-firstapp-dev \
  --query "[0].name" \
  --output tsv

# Configurar variáveis de ambiente
az webapp config appsettings set \
  --resource-group rg-firstapp-dev \
  --name $webAppName \
  --settings \
    DB_HOST=postgres-firstapp-dev.postgres.database.azure.com \
    DB_PORT=5432 \
    DB_NAME=firstappdb \
    DB_USER=dbadmin \
    DB_PASSWORD=<SUA-SENHA> \
    FLASK_ENV=production \
    FLASK_DEBUG=False

# Configurar startup command
az webapp config set \
  --resource-group rg-firstapp-dev \
  --name $webAppName \
  --startup-file "startup.sh"
```

#### Usar Script PowerShell (configure-azure-env.ps1)
```powershell
# Opção 1: Carregar variáveis do .env
Get-Content .env | Where-Object {$_ -and -not $_.StartsWith('#')} | ForEach-Object {
    $k,$v = $_.Split('=',2)
    Set-Item -Path Env:\$k -Value $v
}
.\configure-azure-env.ps1

# Opção 2: Passar parâmetros diretamente
.\configure-azure-env.ps1 `
  -DbHost "postgres-firstapp-dev.postgres.database.azure.com" `
  -DbName "firstappdb" `
  -DbUser "dbadmin" `
  -DbPort 5432
```

### 8.3 Gestão e Monitorização

#### Ver Logs em Tempo Real
```bash
# Stream de logs
az webapp log tail \
  --resource-group rg-firstapp-dev \
  --name $webAppName

# Descarregar logs
az webapp log download \
  --resource-group rg-firstapp-dev \
  --name $webAppName \
  --log-file app_logs.zip
```

#### Restart da Aplicação
```bash
az webapp restart \
  --resource-group rg-firstapp-dev \
  --name $webAppName
```

#### Ver Estado da Aplicação
```bash
# Estado geral
az webapp show \
  --resource-group rg-firstapp-dev \
  --name $webAppName \
  --query "{Name:name, State:state, DefaultHostName:defaultHostName}" \
  --output table

# Verificar app settings
az webapp config appsettings list \
  --resource-group rg-firstapp-dev \
  --name $webAppName \
  --output table
```

### 8.4 Deploy de Código

#### Via Azure Developer CLI (Recomendado)
```bash
# Deploy completo
azd deploy

# Deploy com build verbose
azd deploy --debug
```

#### Via Git (Alternativa)
```bash
# Configurar remote
az webapp deployment source config-local-git \
  --resource-group rg-firstapp-dev \
  --name $webAppName

# Obter credenciais de deployment
az webapp deployment list-publishing-credentials \
  --resource-group rg-firstapp-dev \
  --name $webAppName

# Push para Azure
git remote add azure https://<deployment-user>@<app-name>.scm.azurewebsites.net/<app-name>.git
git push azure main
```

### 8.5 Verificação Pós-Deploy
```bash
# Health check
curl https://app-web-5xuei2n6kwkfk.azurewebsites.net/health

# Inicializar BD
curl https://app-web-5xuei2n6kwkfk.azurewebsites.net/init-db

# Listar utilizadores
curl https://app-web-5xuei2n6kwkfk.azurewebsites.net/users

# Ou via PowerShell
Invoke-WebRequest -Uri "https://app-web-5xuei2n6kwkfk.azurewebsites.net/health" | Select-Object -ExpandProperty Content
```

### 8.6 Limpeza de Recursos

#### Eliminar Resource Group (remove tudo)
```bash
az group delete \
  --name rg-firstapp-dev \
  --yes \
  --no-wait
```

#### Eliminar apenas App Service
```bash
az webapp delete \
  --resource-group rg-firstapp-dev \
  --name $webAppName
```

#### Eliminar PostgreSQL Server
```bash
az postgres flexible-server delete \
  --resource-group rg-firstapp-dev \
  --name postgres-firstapp-dev \
  --yes
```

## 9. Troubleshooting Rápido

| Sintoma | Causa Provável | Ação |
|---------|----------------|------|
| 500 + UnicodeDecodeError | Arquivo não UTF-8 | Executar script conversão / salvar como UTF-8 sem BOM |
| 404 `/init-db` | Código antigo | Pull da branch `main` ou redeploy |
| DB erro ssl | Parametro faltando | Garantir `sslmode=require` na string interna |
| Hook detect-secrets falha | Baseline não adicionada | `git add .secrets.baseline` |
| Password com `@` quebra URL | Não codificada | Usar DB_* ou `%40` |

## 10. Próximos Passos Sugeridos

1. Adicionar CI (GitHub Actions) para rodar pre-commit e testes.
2. Implementar autenticação básica ou JWT.
3. Migrar para SQLAlchemy ORM.
4. Integrar Azure Key Vault para segredos (substituir DB_PASSWORD).
5. Adicionar monitorização (Application Insights).

## 11. Referências

- Flask: https://flask.palletsprojects.com/
- psycopg2: https://www.psycopg.org/
- Azure App Service: https://learn.microsoft.com/azure/app-service/
- Detect Secrets: https://github.com/Yelp/detect-secrets
- Azure Developer CLI: https://learn.microsoft.com/azure/developer/azure-developer-cli/

---
Mantido por: Equipa de exemplo • Atualize esta Wiki à medida que novas práticas forem adicionadas.
