import flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import DatabaseManager
from flask import request, redirect, url_for, flash
from colorama import Fore, Style
from colorama import init
from werkzeug.utils import secure_filename
import urllib.parse
import os
import sys

app = flask.Flask(__name__)

app.secret_key = 'cipherthestorm'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

db = DatabaseManager()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/images'
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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

# manifest.json to make it a web app
@app.route('/manifest.json', methods=['GET'])
def manifest():
    return {

    }

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

        # -----------------------
        # Handle uploaded images
        # -----------------------
        images = request.files.getlist('images')
        saved_filenames = []

        # Save images temporarily
        for file in images:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                saved_filenames.append(filename)  # we'll move them after DB insert

        # -----------------------
        # Add predator to DB
        # -----------------------
        if db.add_predator(name, description, address, phone, email, convicted, socials):
            # Get the last added predator to retrieve its ID
            predator = db.get_all_predators()[-1]
            predator_id = predator['id']

            # Create folder for this predator
            predator_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'predator_{predator_id}')
            os.makedirs(predator_folder, exist_ok=True)

            final_paths = []
            for filename in saved_filenames:
                src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                dst = os.path.join(predator_folder, filename)
                os.rename(src, dst)
                final_paths.append(f'images/predator_{predator_id}/{filename}')

            # Update images in DB
            db.update_predator_images(predator_id, final_paths)

            flash(f'{name} added successfully')
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
            flash(f'ID {predator_id} deleted successfully')
        else:
            flash(f'Failed to delete ID {predator_id}')

    print(f"Deleting ID: {predator_id}")
    
    flash(f'Predator with ID {predator_id} deleted successfully')
    return redirect(url_for('predators'))

@app.route('/predators/view/<int:predator_id>', methods=['GET'])
@login_required
def view_predator(predator_id):
    predators = db.get_all_predators()
    # predator = next((p for p in predators if p['id'] == predator_id), None)
    predator = db.get_predator(predator_id=predator_id)
    if predator:
        return flask.render_template('database/view_db.html', predator=predator, url_parse=urllib.parse.quote)
    else:
        flash(f'ID {predator_id} not found')

@app.route('/predators/edit/<int:predator_id>', methods=['GET', 'POST'])
@login_required
def edit_predator(predator_id):
    predator = db.get_predator(predator_id=predator_id)
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
            images = request.files.getlist('images')
            saved_filenames = []

            # Save images temporarily
            for file in images:
                if file.filename != "":
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if temp_path != "static/images/":
                        file.save(temp_path)
                        # print()
                        saved_filenames.append(file.filename)
                    
            predator_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'predator_{predator_id}')
            os.makedirs(predator_folder, exist_ok=True)

            final_paths = []
            for filename in saved_filenames:
                src = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                dst = os.path.join(predator_folder, filename)
                # os.rename(src, dst)
                final_paths.append(f'images/predator_{predator_id}/{filename}')
                
            predator = db.get_predator(predator_id=predator_id)
            previous_paths = predator['images']
            
            for path in previous_paths:
              final_paths.append(path)
              
            # Update images in DB
            
            db.update_predator_images(predator_id, final_paths)

            flash(f'{name} updated successfully')
            return redirect(url_for('predators'))
        else:
            flash(f'Failed to update {name}')
            return redirect(url_for('edit_predator', predator_id=predator_id))

    return flask.render_template('database/edit_db.html', predator=predator)

if len(sys.argv) == 1:
    sys.argv.append(8080)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=sys.argv[1], debug=True)