import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running on Azure!',
        'version': '1.0'
    })

@app.route('/info')
def info():
    """Application info"""
    return jsonify({
        'app': 'FirstAzureApp',
        'python_version': os.sys.version,
        'environment': os.getenv('ENVIRONMENT', 'production')
    })

if __name__ == '__main__':
    # Get port from environment variable for Azure App Service
    port = int(os.getenv('PORT', 8000))
    # Only enable debug mode when FLASK_DEBUG is explicitly set
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
