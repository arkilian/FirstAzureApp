# -*- coding: utf-8 -*-
"""
Simple PostgreSQL connection test - standalone version
"""
import os
from pathlib import Path

# Load .env file
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print(f"Loading .env from: {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value
                    print(f"  Loaded: {key}")

load_env()

# Test connection
try:
    import psycopg2
    
    # Get individual connection parameters
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    
    print(f"\nConnecting to database...")
    print(f"Host: {db_host}")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    
    # Build connection string with SSL
    conn_string = f"host={db_host} dbname={db_name} user={db_user} password={db_password} port={db_port} sslmode=require"
    
    conn = psycopg2.connect(conn_string)
    print("\n[SUCCESS] Connected to PostgreSQL!")
    
    cursor = conn.cursor()
    
    # Get version
    cursor.execute('SELECT version();')
    print(f"\nDatabase version:\n{cursor.fetchone()[0]}")
    
    # List tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"\nTables in database ({len(tables)}):")
    if tables:
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("  (no tables found)")
    
    cursor.close()
    conn.close()
    print("\n[SUCCESS] Connection test completed!")
    
except ImportError:
    print("\n[ERROR] psycopg2 not installed")
    print("Install with: pip install psycopg2-binary")
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
