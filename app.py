import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    db_status = "healthy"
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
        else:
            db_status = "unhealthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'database': db_status
    })

@app.route('/users')
def get_users():
    """Get all users from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id;')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/init-db')
def init_db():
    """Initialize database with sample table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO users (name, email) 
            VALUES ('João Silva', 'joao@example.com'),
                   ('Maria Santos', 'maria@example.com')
            ON CONFLICT (email) DO NOTHING;
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
