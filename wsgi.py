
import os
import sys

# Ensure backend folder is in python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app import create_app

# Default to production config for WSGI
env = os.environ.get('FLASK_ENV', 'prod') 
app = create_app(env)

if __name__ == "__main__":
    app.run()
