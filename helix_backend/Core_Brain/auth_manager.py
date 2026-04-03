import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class AuthManager:
    def __init__(self, data_file='users_db.json'):
        self.data_file = data_file
        self.users = self._load_users()

    def _load_users(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_users(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def signup(self, email, password, name=""):
        if email in self.users:
            return None, "Email already exists"
        
        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        
        self.users[email] = {
            "id": user_id,
            "name": name,
            "password": hashed_password,
            "created_at": str(uuid.uuid4()) # For simplicity
        }
        self._save_users()
        return user_id, None

    def login(self, email, password):
        user = self.users.get(email)
        if not user or not check_password_hash(user["password"], password):
            return None, "Invalid email or password"
        
        return user["id"], None
