
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app

app = create_app('dev')

with open('routes.txt', 'w') as f:
    f.write(str(app.url_map))
