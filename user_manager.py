import sqlite3
import bcrypt

class UserManager:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            password TEXT NOT NULL
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def register_user(self, email, first_name, last_name, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            query = "INSERT INTO users (email, first_name, last_name, password) VALUES (?, ?, ?, ?)"
            self.conn.execute(query, (email, first_name, last_name, hashed))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, email):
        query = "SELECT * FROM users WHERE email = ?"
        cursor = self.conn.execute(query, (email,))
        result = cursor.fetchone()
        return result

    def validate_login(self, email, password):
        user = self.get_user(email)
        if user:
            stored_hash = user[4]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return user
        return None

    def update_user_info(self, email, first_name, last_name, new_password=None):
        if new_password:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            query = "UPDATE users SET first_name = ?, last_name = ?, password = ? WHERE email = ?"
            self.conn.execute(query, (first_name, last_name, hashed, email))
        else:
            query = "UPDATE users SET first_name = ?, last_name = ? WHERE email = ?"
            self.conn.execute(query, (first_name, last_name, email))
        self.conn.commit()
        return True

if __name__ == "__main__":
    um = UserManager()
    print("Register a new user:")
    email = input("Enter email: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    password = input("Enter password: ")
    if um.register_user(email, first_name, last_name, password):
        print("User registered successfully!")
    else:
        print("Registration failed. Email might already be in use.")

    print("\nLogin:")
    email_login = input("Enter email: ")
    password_login = input("Enter password: ")
    user = um.validate_login(email_login, password_login)
    if user:
        print("Login successful!")
    else:
        print("Login failed. Incorrect email or password.")

