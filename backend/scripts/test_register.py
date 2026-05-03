import time
from app.database.connection import init_db, get_db
from app.services.auth_service import AuthService

# Initialize in-memory DB (mongomock) by passing falsy URI
init_db(None)

a = AuthService()
email = f"testuser+{int(time.time())}@example.com"
print('Registering', email)
resp, status = a.register_user(name='Test User', email=email, password='Passw0rd!')
print('Response:', resp)
print('Status:', status)

db = get_db()
user = db.users.find_one({'email': email})
print('Raw DB entry:', user)
if user:
    print('Inserted id:', str(user.get('_id')))
else:
    print('No user found in DB')
