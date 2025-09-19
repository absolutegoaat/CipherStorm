import mysql.connector
from mysql.connector import Error
import hashlib
from colorama import Fore, Style

class DatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="cipherstorm"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.initialize_database()
    
    def get_connection(self):
        """Return a MySQL connection"""
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
    
    def initialize_database(self):
        """Check if database exists and create tables if needed"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()
            conn.close()
            print(f"{Fore.GREEN}[+] Database '{self.database}' ready.{Style.RESET_ALL}")
            self._create_tables()
        except Error as e:
            print(f"{Fore.RED}[-] Error initializing database: {e}{Style.RESET_ALL}")
            raise

    def _create_tables(self):
        """Create users and predators tables in MySQL"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            ''')

            # Predators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predators (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    address VARCHAR(255),
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    description TEXT,
                    convicted BOOLEAN DEFAULT FALSE,
                    socials TEXT
                )
            ''')
            # Predator images table 
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predator_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    predator_id INT NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    FOREIGN KEY (predator_id) REFERENCES predators(id) ON DELETE CASCADE
                )
            ''')

            conn.commit()
            print(f"{Fore.GREEN}[+] Tables created successfully.{Style.RESET_ALL}")
            self._create_default_users(cursor)
            conn.commit()
            conn.close()
        except Error as e:
            print(f"{Fore.RED}[-] Error creating tables: {e}{Style.RESET_ALL}")
            raise

    def _create_default_users(self, cursor):
        """Insert default admin and test users"""
        admin_password_hash = self._hash_password("admin123")
        cursor.execute('''
            INSERT IGNORE INTO users (username, password_hash, is_admin)
            VALUES (%s, %s, %s)
        ''', ('admin', admin_password_hash, 1))

        user_password_hash = self._hash_password("user123")
        cursor.execute('''
            INSERT IGNORE INTO users (username, password_hash, is_admin)
            VALUES (%s, %s, %s)
        ''', ('testuser', user_password_hash, 0))

        print("Default users created:")
        print("admin (password: admin123) - Admin")
        print("testuser (password: user123) - Regular user")
        print(f"{Fore.YELLOW}[+] Use admin account to manage other users.{Style.RESET_ALL}")

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # -----------------------------
    # User methods
    # -----------------------------
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self._hash_password(password)
            cursor.execute('''
                SELECT id, username, is_admin
                FROM users
                WHERE username = %s AND password_hash = %s
            ''', (username, password_hash))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                self.update_last_login(user_data[0])
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'is_admin': bool(user_data[2])
                }
            return None
        except Error as e:
            print(f"{Fore.RED}[-] Error authenticating user: {e}{Style.RESET_ALL}")
            return None

    def update_last_login(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s', (user_id,))
            conn.commit()
            conn.close()
        except Error as e:
            print(f"{Fore.RED}[-] Error updating last login: {e}{Style.RESET_ALL}")

    def add_user(self, username, password, is_admin=False):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (%s, %s, %s)
            ''', (username, password_hash, int(is_admin)))
            conn.commit()
            conn.close()
            return True
        except mysql.connector.IntegrityError:
            print(f"{Fore.YELLOW}[*] User '{username}' already exists.{Style.RESET_ALL}")
            return False
        except Error as e:
            print(f"{Fore.RED}[-] Error adding user: {e}{Style.RESET_ALL}")
            return False

    def get_user_by_id(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, is_admin FROM users WHERE id = %s', (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {'id': row[0], 'username': row[1], 'is_admin': bool(row[2])}
            return None
        except Error as e:
            print(f"{Fore.RED}[-] Error getting user by ID: {e}{Style.RESET_ALL}")
            return None

    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, is_admin, created_at, last_login FROM users ORDER BY username')
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
        except Error as e:
            print(f"{Fore.RED}[-] Error getting all users: {e}{Style.RESET_ALL}")
            return []

    def edit_user(self, user_id, username=None, password=None, is_admin=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if username:
                cursor.execute('UPDATE users SET username = %s WHERE id = %s', (username, user_id))
            if password:
                password_hash = self._hash_password(password)
                cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
            if is_admin is not None:
                cursor.execute('UPDATE users SET is_admin = %s WHERE id = %s', (int(is_admin), user_id))
            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error editing user: {e}{Style.RESET_ALL}")
            return False

    def delete_user(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error deleting user: {e}{Style.RESET_ALL}")
            return False

    # -----------------------------
    # Predator methods
    # -----------------------------
    
    def add_predator(self, name, description, address=None, phone=None, email=None, convicted=False, socials=None, image_paths=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Insert predator
            cursor.execute(f'''
                INSERT INTO predators (name, description, address, phone, email, convicted, socials)
                VALUES (%s, '{description}', %s, %s, %s, %s, %s)
            ''', (name, address, phone, email, int(convicted), socials))
            predator_id = cursor.lastrowid  # get the new predator's ID

            # Insert images if provided
            if image_paths:
                for path in image_paths:
                    cursor.execute('''
                        INSERT INTO predator_images (predator_id, image_path)
                        VALUES (%s, %s)
                    ''', (predator_id, path))

            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error adding predator: {e}{Style.RESET_ALL}")
            return False

    def get_all_predators(self):
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
                    'socials': row[7]
                })
            return predators
        except Error as e:
            print(f"{Fore.RED}[-] Error getting all predators: {e}{Style.RESET_ALL}")
            return []

    def get_predator(self, predator_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get predator info
            cursor.execute('SELECT * FROM predators WHERE id=%s', (predator_id,))
            row = cursor.fetchone()
            if not row:
                return None

            predator = {
                'id': row[0],
                'name': row[1],
                'address': row[2],
                'phone': row[3],
                'email': row[4],
                'description': row[5],
                'convicted': bool(row[6]),
                'socials': row[7]
            }

            # Get images
            cursor.execute('SELECT image_path FROM predator_images WHERE predator_id=%s', (predator_id,))
            images = [r[0] for r in cursor.fetchall()]
            predator['images'] = images

            conn.close()
            return predator
        except Error as e:
            print(f"{Fore.RED}[-] Error fetching predator: {e}{Style.RESET_ALL}")
            return None

    def update_predator(self, predator_id, name, description, address=None, phone=None, email=None, convicted=False, socials=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE predators
                SET name=%s, description=%s, address=%s, phone=%s, email=%s, convicted=%s, socials=%s
                WHERE id=%s
            ''', (name, description, address, phone, email, int(convicted), socials, predator_id))
            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error updating predator: {e}{Style.RESET_ALL}")
            return False

    def update_predator_images(self, predator_id, new_image_paths):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Delete old images
            cursor.execute('DELETE FROM predator_images WHERE predator_id=%s', (predator_id,))

            # Insert new images
            for path in new_image_paths:
                cursor.execute('INSERT INTO predator_images (predator_id, image_path) VALUES (%s, %s)',
                               (predator_id, path))

            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error updating predator images: {e}{Style.RESET_ALL}")
            return False

    def delete_predator(self, predator_id):
        """
        Delete a predator. Images are deleted automatically in the DB due to ON DELETE CASCADE.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM predators WHERE id = %s', (predator_id,))
            conn.commit()
            conn.close()
            return True
        except Error as e:
            print(f"{Fore.RED}[-] Error deleting predator: {e}{Style.RESET_ALL}")
            return False