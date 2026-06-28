import os

# Manual .env loader helper to avoid external library dependencies
def load_dotenv(dotenv_path=None):
    if not dotenv_path:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

# Load environment variables on startup
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nexthire_ai_quantum_secret_key'
    
    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or 'YOUR_GOOGLE_CLIENT_SECRET'
    
    # MySQL Database credentials
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or ''
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'nexthire'
