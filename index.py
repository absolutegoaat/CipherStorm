import flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
import hashlib
import requests
from flask import request, redirect, url_for, flash
from colorama import Fore, Style
from colorama import init
from werkzeug.utils import secure_filename



app = flask.Flask(__name__)

app.secret_key = 'cipherthestorm'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

class DatabaseManager:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.initialize_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Check if database exists, if not create it with default schema."""
        db_exists = os.path.exists(self.db_path)
        
        if not db_exists:
            print(f"{Fore.YELLOW}[*] Database '{self.db_path}' not found. Creating new database...{Style.RESET_ALL}")
            self._create_database()
        else:
            print(f"{Fore.GREEN}[*] Database '{self.db_path}' already exists.{Style.RESET_ALL}")
    
    def _create_database(self):
        """Create new database with users table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # creates tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    description TEXT,
                    convicted BOOLEAN DEFAULT 0,
                    socials TEXT,
                );''')
            
            conn.commit()
            print(f"{Fore.GREEN}[+] Database schema created successfully.{Style.RESET_ALL}")
            
            # Insert default admin user
            self._create_default_users(cursor)
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error creating database: {e}{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"{Fore.RED}[-] Unexpected error: {e}{Style.RESET_ALL}")
            raise

    def _create_default_users(self, cursor):
        # Default admin user
        admin_password_hash = self._hash_password("admin123")
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', ('ralsei', admin_password_hash, 1))
        
        # Regular User Test
        user_password_hash = self._hash_password("user123")
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', ('testuser', user_password_hash, 0))
        
        print("Default users created:")
        print("hunter (password: admin123) - Admin")
        print("testuser (password: user123) - Regular user")
        print(f"{Fore.YELLOW}[+] In order to manage other users please use the admin account.{Style.RESET_ALL}")
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                SELECT id, username, is_admin 
                FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                # Update last login
                self.update_last_login(user_data[0])
                
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'is_admin': bool(user_data[2])
                }
            return None
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error authenticating user: {e}{Style.RESET_ALL}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, is_admin 
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'is_admin': bool(user_data[2])
                }
            return None
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error getting user by ID: {e}{Style.RESET_ALL}")
            return None
    
    def update_last_login(self, user_id):
        """Update user's last login time."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error updating last login: {e}{Style.RESET_ALL}")
    
    def get_all_users(self):
        """Get all users (for admin purposes)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, is_admin, created_at, last_login 
                FROM users 
                ORDER BY username
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'is_admin': bool(row[2]),
                    'created_at': row[3],
                    'last_login': row[4]
                })
            
            return users
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error getting all users: {e}{Style.RESET_ALL}")
            return []
    
    def add_user(self, username, password, is_admin=False):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self._hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            ''', (username, password_hash, int(is_admin)))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            print(f"{Fore.YELLOW}[*] User '{username}' already exists.{Style.RESET_ALL}")
            return False
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error adding user: {e}{Style.RESET_ALL}")
            return False
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error adding user: {e}{Style.RESET_ALL}")
            return 
        
    def add_predator(self, name, description, address=None, phone=None, email=None, convicted=False, socials=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predators (name, description, address, phone, email, convicted, socials)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, address, phone, email, int(convicted), socials))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error adding predator: {e}{Style.RESET_ALL}")
            return False
        
    def get_all_predators(self):
        """
        Get all predators from the database.

        Returns:
            list: List of dictionaries containing predator data.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM predators')
            rows = cursor.fetchall()
            conn.close()
            
            predators = []
            for row in rows:
                predators.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'phone': row[3],
                    'email': row[4],
                    'description': row[5],
                    'convicted': bool(row[6]),
                    'socials': row[7],
                })
            
            return predators
            
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error getting all predators: {e}{Style.RESET_ALL}")
            return []
    
    def delete_predator(self, predator_id):
        """
        Delete a predator by ID.

        Args:
            predator_id (int): The ID of the predator to delete.

        Returns:
            bool: True if the predator was deleted successfully, False otherwise.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM predators WHERE id = ?', (predator_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error deleting predator: {e}{Style.RESET_ALL}")
            return False
        
    def delete_user(self, user_id):
        """
        Delete a user by ID.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if the user was deleted successfully, False otherwise.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error deleting user: {e}{Style.RESET_ALL}")
            return False
        
    def edit_user(self, user_id, username=None, password=None, is_admin=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if username:
                cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
            if password:
                password_hash = self._hash_password(password)
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            if is_admin is not None:
                cursor.execute('UPDATE users SET is_admin = ? WHERE id = ?', (int(is_admin), user_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error editing user: {e}{Style.RESET_ALL}")
            return False
        
    def update_predator(self, predator_id, name, description, address=None, phone=None, email=None, convicted=False, socials=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE predators
                SET name = ?, description = ?, address = ?, phone = ?, email = ?, convicted = ?, socials = ?
                WHERE id = ?
            ''', (name, description, address, phone, email, int(convicted), socials, predator_id))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"{Fore.RED}[-] Error updating predator: {e}{Style.RESET_ALL}")
            return False

        
# Initialize database
db = DatabaseManager()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.is_admin = user_data['is_admin']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None

# Login route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       
        # Check for empty fields first
        if not username or not password:
            print(f'{Fore.RED}[-] Login attempt with empty username or password{Fore.RESET_ALL}')
            flash('Please enter both username and password')
            return redirect(url_for('login'))
       
        # Authenticate with database
        user_data = db.authenticate_user(username, password)
        if user_data:
            print(f"{Fore.GREEN}[+] User {username} logged in successfully{Style.RESET_ALL}")
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            print(f"{Fore.RED}[-] Invalid login attempt: {username}{Style.RESET_ALL}")
            flash('Invalid credentials')
            return redirect(url_for('index'))
        
    return flask.render_template('index.html')

@app.route('/ralsei')
def ralsei():
    return flask.render_template('fun/ralsei.html')

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return flask.render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    if user.is_admin:
        return flask.render_template('home.html')
    elif user.is_authenticated:
        return flask.render_template('home.html')
    else:
        flash('Access denied.')
        return redirect(url_for('index'))
    
@app.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
    user = current_user
    if user.is_admin:
        users = db.get_all_users()
        return flask.render_template('admin/users.html', users=users)
    else:
        flash('Access denied.')
        return redirect(url_for('index'))
    
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    user = current_user
    if not user.is_admin:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = 'is_admin' in request.form
        
        if not username or not password:
            flash('Username and password cannot be empty')
            return redirect(url_for('manage_users'))

        if db.add_user(username, password, is_admin):
            flash(f'User {username} added successfully')
        else:
            flash(f'Failed to add user {username}')
        
        return redirect(url_for('manage_users'))

    return flask.render_template('admin/add_user.html')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = current_user
    if not user.is_admin:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    if db.delete_user(user_id):
        flash(f'User with ID {user_id} deleted successfully')
    else:
        flash(f'Failed to delete user with ID {user_id}')
    
    return redirect(url_for('manage_users'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user_edit = db.get_user_by_id(user_id)  # <-- you need this function in your db module
    user = current_user
    if not user.is_admin:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        is_admin = 'is_admin' in request.form
        
        if not username or not password:
            flash('Username and password cannot be empty')
            return redirect(url_for('edit_user', user_id=user_id))

        if db.edit_user(user_id, username, password, is_admin):
            flash(f'User {username} updated successfully')
        else:
            flash(f'Failed to update user {username}')
        
        return redirect(url_for('manage_users'))

    return flask.render_template('admin/edit_user.html', user_edit=user_edit)

@app.route('/predators', methods=['GET'])
@login_required
def predators():
    predators = db.get_all_predators()
    return flask.render_template('database/db.html', predators=predators)

@app.route('/predators/add', methods=['GET', 'POST'])
@login_required
def add_predator():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        description = request.form.get('description', '').strip()
        socials = request.form.get('socials', '').strip()
        convicted = request.form.get('convicted', 'off') == 'on'

        if not name or not description:
            flash('Name name Description are required.')
            return redirect(url_for('add_predator'))

        if db.add_predator(name, description, address, phone, email, convicted, socials):
            flash(f'Predator {name} added successfully')
            return redirect(url_for('predators'))
        else:
            flash(f'Failed to add predator {name}')
            return redirect(url_for('add_predator'))
        
    return flask.render_template('database/add_db.html')

@app.route('/predators/delete/<int:predator_id>', methods=['POST'])
@login_required
def delete_predator(predator_id):
    if request.method == 'POST':
        if db.delete_predator(predator_id):
            flash(f'Predator with ID {predator_id} deleted successfully')
        else:
            flash(f'Failed to delete predator with ID {predator_id}')

    print(f"Deleting predator with ID: {predator_id}")
    
    flash(f'Predator with ID {predator_id} deleted successfully')
    return redirect(url_for('predators'))

@app.route('/predators/view/<int:predator_id>', methods=['GET'])
@login_required
def view_predator(predator_id):
    predators = db.get_all_predators()
    predator = next((p for p in predators if p['id'] == predator_id), None)
    if predator:
        return flask.render_template('database/view_db.html', predator=predator)
    else:
        flash(f'Predator with ID {predator_id} not found')

@app.route('/predators/edit/<int:predator_id>', methods=['GET', 'POST'])
@login_required
def edit_predator(predator_id):
    predator = next((p for p in db.get_all_predators() if p['id'] == predator_id), None)
    if not predator:
        flash(f'Predator with ID {predator_id} not found')
        return redirect(url_for('predators'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        description = request.form.get('description', '').strip()
        convicted = request.form.get('convicted', 'off') == 'on'
        socials = request.form.get('socials', '').strip()

        if not name or not description:
            flash('Name and Description are required.')
            return redirect(url_for('edit_predator', predator_id=predator_id))

        if db.update_predator(predator_id, name, description, address, phone, email, convicted, socials):
            flash(f'Predator {name} updated successfully')
            return redirect(url_for('predators'))
        else:
            flash(f'Failed to update predator {name}')
            return redirect(url_for('edit_predator', predator_id=predator_id))

    return flask.render_template('database/edit_db.html', predator=predator)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)