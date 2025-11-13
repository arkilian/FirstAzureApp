# FirstAzureApp ðŸš€

Primeira aplicaÃ§Ã£o Azure com Python 3.13 e PostgreSQL!

## ðŸ“‹ DescriÃ§Ã£o

Esta Ã© uma aplicaÃ§Ã£o web desenvolvida com Flask que demonstra a integraÃ§Ã£o entre Python e PostgreSQL na Azure. A aplicaÃ§Ã£o inclui:

- âœ… API REST com Flask
- âœ… ConexÃ£o com PostgreSQL
- âœ… Interface web interativa
- âœ… Endpoints para gestÃ£o de utilizadores
- âœ… Health checks
- âœ… Pronta para deploy na Azure

## ðŸ› ï¸ Tecnologias

- **Python 3.13** - Linguagem de programaÃ§Ã£o
- **Flask** - Framework web
- **PostgreSQL** - Base de dados
- **psycopg2** - Driver PostgreSQL para Python
- **Gunicorn** - Servidor WSGI para produÃ§Ã£o
- **Azure App Service** - Plataforma de hospedagem

## ðŸ“¦ InstalaÃ§Ã£o Local

### PrÃ©-requisitos

- Python 3.13 ou superior
- PostgreSQL instalado e em execuÃ§Ã£o
- pip (gestor de pacotes Python)

### Passos

1. **Clone o repositÃ³rio:**
   ```bash
   git clone https://github.com/arkilian/FirstAzureApp.git
   cd FirstAzureApp
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependÃªncias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variÃ¡veis de ambiente:**
   ```bash
   cp .env.example .env
   ```
   
   Edite o ficheiro `.env` com as suas credenciais PostgreSQL:
   ```
   DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/firstazureapp
   ```

5. **Crie a base de dados:**
   ```bash
   # No PostgreSQL, execute:
   createdb firstazureapp
   ```

6. **Execute a aplicaÃ§Ã£o:**
   ```bash
   python app.py
   ```

7. **Acesse no navegador:**
   ```
   http://localhost:8000
   ```

## ðŸš€ Deploy na Azure

### OpÃ§Ã£o 1: Azure CLI

1. **Instale a Azure CLI:**
   ```bash
   # Siga as instruÃ§Ãµes em: https://docs.microsoft.com/cli/azure/install-azure-cli
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

7. **Configure a variÃ¡vel de ambiente:**
   ```bash
   az webapp config appsettings set \
     --resource-group FirstAzureAppRG \
     --name firstazureapp \
     --settings DATABASE_URL="postgresql://azureuser:<senha>@firstazureapp-db.postgres.database.azure.com:5432/firstazureapp"
   ```

8. **Configure o comando de startup:**
   ```bash
   az webapp config set \
     --resource-group FirstAzureAppRG \
     --name firstazureapp \
     --startup-file "startup.sh"
   ```

### OpÃ§Ã£o 2: Visual Studio Code

1. Instale a extensÃ£o "Azure App Service"
2. FaÃ§a login na sua conta Azure
3. Clique com o botÃ£o direito na pasta do projeto
4. Selecione "Deploy to Web App"
5. Siga as instruÃ§Ãµes do assistente

## ðŸ“š Endpoints da API

| MÃ©todo | Endpoint | DescriÃ§Ã£o |
|--------|----------|-----------|
| GET | `/` | PÃ¡gina inicial com interface web |
| GET | `/health` | Verificar estado da aplicaÃ§Ã£o e BD |
| GET | `/init-db` | Inicializar a base de dados com dados de exemplo |
| GET | `/users` | Listar todos os utilizadores |

## ðŸ§ª Testar a AplicaÃ§Ã£o

1. Acesse a pÃ¡gina inicial: `http://localhost:8000` ou `https://seu-app.azurewebsites.net`
2. Clique em "Verificar SaÃºde" para testar a conexÃ£o
3. Clique em "Inicializar BD" para criar a tabela e dados de exemplo
4. Clique em "Listar Utilizadores" para ver os dados

## ðŸ“ Estrutura do Projeto

```
FirstAzureApp/
â”‚
â”œâ”€â”€ app.py              # AplicaÃ§Ã£o Flask principal
â”œâ”€â”€ requirements.txt    # DependÃªncias Python
â”œâ”€â”€ startup.sh         # Script de startup para Azure
â”œâ”€â”€ azure.yaml         # ConfiguraÃ§Ã£o Azure
â”œâ”€â”€ .env.example       # Exemplo de variÃ¡veis de ambiente
â”œâ”€â”€ .gitignore         # Ficheiros a ignorar no Git
â”œâ”€â”€ README.md          # Este ficheiro
â”‚
â””â”€â”€ templates/
    â””â”€â”€ index.html     # Template HTML da pÃ¡gina inicial
```

## ðŸ”§ Desenvolvimento

### Adicionar novos endpoints

Edite `app.py` e adicione novas rotas:

```python
@app.route('/novo-endpoint')
def novo_endpoint():
    return jsonify({'mensagem': 'OlÃ¡!'})
```

### Modificar a base de dados

Edite a funÃ§Ã£o `init_db()` em `app.py` para adicionar novas tabelas ou dados.

## ðŸ” SeguranÃ§a

- âš ï¸ Nunca commit o ficheiro `.env` com credenciais reais
- ðŸ”’ Use senhas fortes para a base de dados
- ðŸ›¡ï¸ Configure as regras de firewall do PostgreSQL na Azure
- ðŸ”‘ Use Azure Key Vault para armazenar segredos em produÃ§Ã£o

## ðŸ› ResoluÃ§Ã£o de Problemas

### Erro de conexÃ£o com a base de dados

- Verifique se o PostgreSQL estÃ¡ a correr
- Confirme as credenciais no ficheiro `.env`
- Na Azure, verifique as regras de firewall do servidor PostgreSQL

### Erro ao instalar psycopg2

Se tiver problemas a instalar `psycopg2`, tente:
```bash
pip install psycopg2-binary
```

## ðŸ“ LicenÃ§a

Este projeto Ã© open source e estÃ¡ disponÃ­vel sob a licenÃ§a MIT.

## ðŸ‘¨â€ðŸ’» Autor

Desenvolvido como exemplo de primeira aplicaÃ§Ã£o Azure com Python e PostgreSQL.

## ðŸ¤ ContribuiÃ§Ãµes

ContribuiÃ§Ãµes sÃ£o bem-vindas! Sinta-se Ã  vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## ðŸ“ž Suporte

Para questÃµes e suporte:
- Crie uma issue no GitHub
- Consulte a documentaÃ§Ã£o da Azure: https://docs.microsoft.com/azure/

---

â­ Se este projeto foi Ãºtil, considere dar uma estrela no GitHub!
