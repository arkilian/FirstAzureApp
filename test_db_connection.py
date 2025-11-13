# -*- coding: utf-8 -*-
"""
Test script for PostgreSQL database connection
Run this script to verify database connectivity and diagnose connection issues
"""
import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"[WARNING] .env file not found at: {env_path}")
        print("Create a .env file with your database credentials")
        return False
    
    print(f"[INFO] Loading variables from: {env_path}")
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    os.environ[key] = value
                    print(f"  Loaded: {key}")
        
        print("[OK] .env file loaded successfully\n")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to load .env file: {e}")
        return False


def parse_database_url():
    """Parse DATABASE_URL and set individual DB_ variables"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        return
    
    print("[INFO] Found DATABASE_URL, parsing connection details...")
    
    try:
        # Parse postgresql://user:password@host:port/database?params
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(database_url)
        
        db_user = parsed.username
        db_password = parsed.password
        db_host = parsed.hostname
        db_port = str(parsed.port) if parsed.port else '5432'
        db_name = parsed.path.lstrip('/')
        
        # Set individual variables if not already set
        if not os.getenv('DB_USER'):
            os.environ['DB_USER'] = db_user
        if not os.getenv('DB_PASSWORD'):
            os.environ['DB_PASSWORD'] = db_password
        if not os.getenv('DB_HOST'):
            os.environ['DB_HOST'] = db_host
        if not os.getenv('DB_PORT'):
            os.environ['DB_PORT'] = db_port
        if not os.getenv('DB_NAME'):
            os.environ['DB_NAME'] = db_name
        
        print(f"  Parsed: {db_user}@{db_host}:{db_port}/{db_name}")
        
    except Exception as e:
        print(f"[WARNING] Could not parse DATABASE_URL: {e}")

def test_psycopg2_connection():
    """Test connection using psycopg2 (traditional driver)"""
    try:
        import psycopg2
        from psycopg2 import sql
        
        print("[OK] psycopg2 package imported successfully")
        
        # Get connection parameters from environment variables
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'postgres')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_port = os.getenv('DB_PORT', '5432')
        
        print(f"\nConnection parameters:")
        print(f"  Host: {db_host}")
        print(f"  Database: {db_name}")
        print(f"  User: {db_user}")
        print(f"  Port: {db_port}")
        print(f"  Password: {'*' * len(db_password) if db_password else '(not set)'}")
        
        print("\nAttempting to connect...")
        
        # Connection string approach
        conn_string = f"host={db_host} dbname={db_name} user={db_user} password={db_password} port={db_port}"
        
        conn = psycopg2.connect(conn_string)
        print("[OK] Connection successful using psycopg2!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"\nPostgreSQL version: {db_version[0]}")
        
        cursor.close()
        conn.close()
        print("[OK] Connection closed successfully")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] psycopg2 not installed: {e}")
        print("  Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"[ERROR] Connection failed with psycopg2: {type(e).__name__}")
        print(f"  Error: {e}")
        return False


def test_sqlalchemy_connection():
    """Test connection using SQLAlchemy"""
    try:
        from sqlalchemy import create_engine, text
        
        print("\n" + "="*60)
        print("Testing with SQLAlchemy")
        print("="*60)
        print("[OK] sqlalchemy package imported successfully")
        
        # Get connection parameters
        db_host = os.getenv('DB_HOST', 'localhost')
        db_name = os.getenv('DB_NAME', 'postgres')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        db_port = os.getenv('DB_PORT', '5432')
        
        # Create connection URL
        connection_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        print(f"\nConnection URL (masked): postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        
        print("\nAttempting to connect...")
        engine = create_engine(connection_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()
            print("[OK] Connection successful using SQLAlchemy!")
            print(f"\nPostgreSQL version: {db_version[0]}")
        
        engine.dispose()
        print("[OK] Connection closed successfully")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] SQLAlchemy not installed: {e}")
        print("  Install with: pip install sqlalchemy psycopg2-binary")
        return False
    except Exception as e:
        print(f"[ERROR] Connection failed with SQLAlchemy: {type(e).__name__}")
        print(f"  Error: {e}")
        return False


def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n" + "="*60)
    print("Checking Environment Variables")
    print("="*60)
    
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    optional_vars = ['DB_PORT']
    
    all_set = True
    
    print("\nRequired variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"  [OK] {var} = {'*' * len(value)}")
            else:
                print(f"  [OK] {var} = {value}")
        else:
            print(f"  [MISSING] {var} = (not set)")
            all_set = False
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var, '5432')
        print(f"  [INFO] {var} = {value}")
    
    if not all_set:
        print("\n[WARNING] Some required environment variables are not set")
        print("\nYou can set them in your terminal:")
        print("  $env:DB_HOST='your-server.postgres.database.azure.com'")
        print("  $env:DB_NAME='your_database'")
        print("  $env:DB_USER='your_user'")
        print("  $env:DB_PASSWORD='your_password'")
        print("  $env:DB_PORT='5432'")
    
    return all_set


def main():
    """Main test function"""
    print("="*60)
    print("PostgreSQL Connection Test")
    print("="*60)
    
    # Load .env file
    load_env_file()
    
    # Parse DATABASE_URL if present
    parse_database_url()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n[FAIL] Cannot proceed without required environment variables")
        sys.exit(1)
    
    # Test with psycopg2
    print("\n" + "="*60)
    print("Testing with psycopg2")
    print("="*60)
    psycopg2_ok = test_psycopg2_connection()
    
    # Test with SQLAlchemy
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"psycopg2:   {'[PASS]' if psycopg2_ok else '[FAIL]'}")
    print(f"SQLAlchemy: {'[PASS]' if sqlalchemy_ok else '[FAIL]'}")
    
    if psycopg2_ok or sqlalchemy_ok:
        print("\n[SUCCESS] Database connection is working!")
    else:
        print("\n[FAIL] Database connection failed. Check the errors above.")
        print("\nCommon issues:")
        print("  1. Incorrect credentials (username/password)")
        print("  2. Firewall blocking connection (check Azure firewall rules)")
        print("  3. SSL/TLS requirements (Azure PostgreSQL requires SSL)")
        print("  4. Network connectivity issues")
        print("  5. Database server not running or not accessible")


if __name__ == "__main__":
    main()
