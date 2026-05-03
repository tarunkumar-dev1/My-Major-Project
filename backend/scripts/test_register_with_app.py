import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app import create_app
from config import Config
from app.database.connection import get_db
from app.services.auth_service import AuthService

app = create_app(Config)
with app.app_context():
    # create_app calls init_db already inside app_context
    a = AuthService()
    resp, status = a.register_user(name='AppContext Tester', email='appctx_test@example.com', password='Passw0rd!')
    print('Response:', resp)
    print('Status:', status)

    db = get_db()
    user = db.users.find_one({'email': 'appctx_test@example.com'})
    print('DB found:', bool(user))
    if user:
        print('User id:', str(user['_id']))
