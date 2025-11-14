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
   - Operações CRUD básicas
   - Gestão de utilizadores

3. **Interface Web**
   - Design moderno e responsivo
   - Gradientes e animações CSS
   - Interação em tempo real com a API

4. **Pronto para Produção**
   - Configuração Gunicorn
   - Gestão de variáveis de ambiente
   - Scripts de deploy Azure

## 📋 Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL (local ou Azure)
- Conta Azure (para deploy)
- Git

## 🚀 Deploy Rápido

### 1. Preparação Local

```bash
# Clone o repositório
git clone https://github.com/arkilian/FirstAzureApp.git
cd FirstAzureApp

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração PostgreSQL

#### Opção A: PostgreSQL Local

```bash
# Crie a base de dados
createdb firstazureapp

# Configure o .env
cp .env.example .env
```

Edite `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=firstazureapp
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

#### Opção B: Azure PostgreSQL

```bash
# Crie servidor PostgreSQL no Azure
az postgres flexible-server create \
  --resource-group FirstAzureAppRG \
  --name firstazureapp-db \
  --location westeurope \
  --admin-user azureuser \
  --admin-password <SUA-SENHA-SEGURA> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

# Crie a base de dados
az postgres flexible-server db create \
  --resource-group FirstAzureAppRG \
  --server-name firstazureapp-db \
  --database-name firstazureapp

# Configure regras de firewall
az postgres flexible-server firewall-rule create \
  --resource-group FirstAzureAppRG \
  --name firstazureapp-db \
  --rule-name AllowAllAzureIPs \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 3. Deploy no Azure App Service

```bash
# Login no Azure
az login

# Deploy direto
az webapp up \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --runtime "PYTHON:3.11" \
  --sku B1

# Configure variáveis de ambiente
az webapp config appsettings set \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --settings DATABASE_URL="postgresql://azureuser:<SENHA>@firstazureapp-db.postgres.database.azure.com:5432/firstazureapp"

# Configure startup command
az webapp config set \
  --resource-group FirstAzureAppRG \
  --name firstazureapp \
  --startup-file "startup.sh"
```

## 🔧 Estrutura do Código

### app.py

```python
from flask import Flask, render_template, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    # Verifica conexão com base de dados
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except:
        return jsonify({
            'status': 'healthy',
            'database': 'error'
        }), 500

@app.route('/init-db')
def init_db():
    # Cria tabela e dados iniciais
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        )
    ''')

    cur.execute('''
        INSERT INTO users (name, email) VALUES
        ('João Silva', 'joao@example.com'),
        ('Maria Santos', 'maria@example.com')
        ON CONFLICT DO NOTHING
    ''')

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Base de dados inicializada!'})

@app.route('/users')
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({'users': users})

if __name__ == '__main__':
    app.run(debug=True)
```

## 🎨 Personalização

### Modificar Cores

Edite `templates/index.html`:
```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Adicionar Novos Endpoints

```python
@app.route('/api/novo-endpoint')
def novo_endpoint():
    return jsonify({'mensagem': 'Seu novo endpoint!'})
```

### Modificar Tabelas

```python
@app.route('/init-db')
def init_db():
    # Adicione suas tabelas aqui
    cur.execute('''
        CREATE TABLE IF NOT EXISTS seus_dados (
            id SERIAL PRIMARY KEY,
            campo1 VARCHAR(100),
            campo2 TEXT
        )
    ''')
```

## 🔒 Segurança

### Melhores Práticas Implementadas

1. **Nunca commitar .env** - use sempre Azure Key Vault ou variáveis de ambiente
2. **SSL/TLS** - conexões encriptadas com PostgreSQL
3. **Variáveis de ambiente** - credenciais nunca no código
4. **CORS** - configure conforme necessário

### Para Produção

```python
# Adicione ao app.py
from flask_cors import CORS
from flask_talisman import Talisman

CORS(app, origins=['https://seu-dominio.com'])
Talisman(app, force_https=True)
```

## 📊 Monitorização

### Application Insights

```bash
# Adicione ao requirements.txt
opencensus-ext-azure
opencensus-ext-flask

# Configure no app.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=<SUA-KEY>'
))
```

### Logs no Azure

```bash
# Ver logs em tempo real
az webapp log tail --name firstazureapp --resource-group FirstAzureAppRG
```

## 🧪 Testes

### Teste Local

```bash
python app.py
# Acesse http://localhost:5000
```

### Teste Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Inicializar BD
curl http://localhost:5000/init-db

# Listar utilizadores
curl http://localhost:5000/users
```

## 🎯 Próximos Passos

1. **Autenticação** - Adicione Azure AD B2C
2. **Cache** - Implemente Azure Redis Cache
3. **Storage** - Integre Azure Blob Storage
4. **CI/CD** - Configure GitHub Actions
5. **Domínio Custom** - Configure DNS e certificado SSL

## 📚 Recursos

- [Documentação Flask](https://flask.palletsprojects.com/)
- [Azure App Service Python](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [PostgreSQL Azure](https://docs.microsoft.com/azure/postgresql/)
- [Azure CLI](https://docs.microsoft.com/cli/azure/)

---

Desenvolvido como exemplo de aplicação Python + PostgreSQL no Azure 🚀
