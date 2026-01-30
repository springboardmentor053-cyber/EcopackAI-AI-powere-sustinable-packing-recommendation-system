import os
from dotenv import load_dotenv

# Load .env from project root
# current file is backend/run.py, so root is ../
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

from app import create_app

env = os.environ.get('FLASK_ENV', 'dev')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
