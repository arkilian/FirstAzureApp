from flask import Flask, jsonify, render_template
import os

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
        'message': 'Application is running!'
    })

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'python_version': os.sys.version
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
