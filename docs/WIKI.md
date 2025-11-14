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

## 8. Fluxo de Deploy Azure (Resumo)

```bash
az login
azd env new dev
azd deploy
az webapp config appsettings set \
  --resource-group <rg> \
  --name <app> \
  --settings DB_HOST=<fqdn> DB_PORT=5432 DB_NAME=<db> DB_USER=<user> DB_PASSWORD=<pass>
```
Verificação pós-deploy:
```bash
curl https://<app>.azurewebsites.net/health
curl https://<app>.azurewebsites.net/init-db
curl https://<app>.azurewebsites.net/users
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
