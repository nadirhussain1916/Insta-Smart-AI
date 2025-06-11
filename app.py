from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import requests
import sqlite3
import logging
import secrets
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_auth.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Instagram App Configuration
INSTAGRAM_APP_ID = "743367221597179"
INSTAGRAM_APP_SECRET = "32675a6c834cafff1ee86bad0ae2f38b"
REDIRECT_URI = "http://localhost:5000/auth/callback"

# Instagram Basic Display requires specific configuration
INSTAGRAM_BASIC_DISPLAY_URL = "https://api.instagram.com/oauth/authorize"

# Database setup
def init_db():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('instagram_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instagram_id TEXT UNIQUE NOT NULL,
                username TEXT,
                account_type TEXT,
                access_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def save_user(user_data, access_token):
    """Save user data to database"""
    try:
        conn = sqlite3.connect('instagram_users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (instagram_id, username, account_type, access_token)
            VALUES (?, ?, ?, ?)
        ''', (
            user_data['id'],
            user_data.get('username', ''),
            user_data.get('account_type', ''),
            access_token
        ))
        conn.commit()
        conn.close()
        logger.info(f"User {user_data.get('username')} saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save user: {e}")
        return False

@app.route('/')
def index():
    """Home page with Instagram login button"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instagram Auth</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
            }
            .btn {
                background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: transform 0.3s;
            }
            .btn:hover {
                transform: scale(1.05);
            }
            h1 { color: #333; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Instagram Authentication</h1>
            <a href="/auth/login" class="btn">Continue with Instagram</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route('/auth/login')
def login():
    """Redirect to Instagram authorization"""
    logger.info("Initiating Instagram login")
    
    # Instagram Basic Display API authorization URL
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user_profile,user_media"
        f"&response_type=code"
    )
    
    logger.info(f"Redirecting to Instagram Basic Display auth: {auth_url}")
    return redirect(auth_url)

@app.route('/auth/callback')
def callback():
    """Handle Instagram callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        logger.error(f"Instagram auth error: {error}")
        return render_error(f"Authentication failed: {error}")
    
    if not code:
        logger.error("No authorization code received")
        return render_error("No authorization code received")
    
    logger.info(f"Received authorization code: {code[:10]}...")
    
    # Exchange code for access token
    try:
        token_response = requests.post('https://api.instagram.com/oauth/access_token', data={
            'client_id': INSTAGRAM_APP_ID,
            'client_secret': INSTAGRAM_APP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'code': code
        })
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return render_error("Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        user_id = token_data.get('user_id')
        
        if not access_token:
            logger.error("No access token in response")
            return render_error("No access token received")
        
        logger.info(f"Access token obtained for user: {user_id}")
        
        # Get user profile
        profile_response = requests.get(
            f"https://graph.instagram.com/{user_id}",
            params={
                'fields': 'id,username,account_type',
                'access_token': access_token
            }
        )
        
        if profile_response.status_code != 200:
            logger.error(f"Profile fetch failed: {profile_response.text}")
            return render_error("Failed to fetch user profile")
        
        user_data = profile_response.json()
        logger.info(f"User profile fetched: {user_data.get('username')}")
        
        # Save to database
        if save_user(user_data, access_token):
            return render_success(user_data)
        else:
            return render_error("Failed to save user data")
            
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return render_error("Network error occurred")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render_error("An unexpected error occurred")

def render_success(user_data):
    """Render success page"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Success - Instagram Auth</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            .success { color: #28a745; }
            .user-info { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 5px; 
                margin: 20px 0;
                text-align: left;
            }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">✓ Authentication Successful!</h1>
            <div class="user-info">
                <strong>User Details:</strong><br>
                ID: {{ user_data.id }}<br>
                Username: {{ user_data.username }}<br>
                Account Type: {{ user_data.account_type }}
            </div>
            <p>Your data has been saved successfully.</p>
            <a href="/">← Back to Home</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template, user_data=user_data)

def render_error(error_message):
    """Render error page"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error - Instagram Auth</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            .error { color: #dc3545; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="error">✗ Authentication Failed</h1>
            <p>{{ error_message }}</p>
            <p>Please try again.</p>
            <a href="/">← Back to Home</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template, error_message=error_message)

@app.route('/users')
def list_users():
    """API endpoint to list all authenticated users"""
    try:
        conn = sqlite3.connect('instagram_users.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT instagram_id, username, account_type, created_at FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(users)
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

if __name__ == '__main__':
    init_db()
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)