# -*- coding: utf-8 -*-
import os
from pathlib import Path
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

# Load .env file
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value

load_env()

app = Flask(__name__)

# Database connection helper
def get_db_connection():
    """Create and return a database connection"""
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')

    if not all([db_host, db_name, db_user, db_password]):
        raise ValueError('Database credentials not found in environment variables')

    # Build connection string with SSL required for Azure PostgreSQL
    conn_string = f"host={db_host} dbname={db_name} user={db_user} password={db_password} port={db_port} sslmode=require"

    return psycopg2.connect(conn_string)

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'message': 'Application is running on Azure!',
        'version': '1.0',
        'database': 'not checked'
    }

    # Try to check database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1;')
        cursor.close()
        conn.close()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = 'error'
        status['database_error'] = str(e)

    return jsonify(status)

@app.route('/info')
def info():
    """Application info"""
    return jsonify({
        'app': 'FirstAzureApp',
        'python_version': os.sys.version,
        'environment': os.getenv('ENVIRONMENT', 'production')
    })

@app.route('/db/test')
def test_db():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'database_version': db_version
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/db/tables')
def list_tables():
    """List all tables in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'tables': tables,
            'count': len(tables)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/init-db')
def init_db():
    """Initialize database with users table and sample data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert sample data
        cursor.execute("""
            INSERT INTO users (name, email)
            VALUES
                ('Jo�o Silva', 'joao@example.com'),
                ('Maria Santos', 'maria@example.com'),
                ('Pedro Costa', 'pedro@example.com')
            ON CONFLICT (email) DO NOTHING;
        """)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Base de dados inicializada com sucesso!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/users')
def get_users():
    """Get all users from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, name, email, created_at FROM users ORDER BY id;')
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert datetime objects to strings
        for user in users:
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()

        return jsonify({
            'status': 'success',
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable for Azure App Service
    port = int(os.getenv('PORT', 8000))
    # Only enable debug mode when FLASK_DEBUG is explicitly set
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
