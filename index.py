import flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import DatabaseManager
from flask import request, redirect, url_for, flash
from colorama import Fore, Style
from colorama import init

app = flask.Flask(__name__)

app.secret_key = 'cipherthestorm'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

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

        if db.add_predator(name, description, address, phone, email, convicted, socials):
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
    predator = next((p for p in predators if p['id'] == predator_id), None)
    if predator:
        return flask.render_template('database/view_db.html', predator=predator)
    else:
        flash(f'ID {predator_id} not found')

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
            flash(f'{name} updated successfully')
            return redirect(url_for('predators'))
        else:
            flash(f'Failed to update {name}')
            return redirect(url_for('edit_predator', predator_id=predator_id))

    return flask.render_template('database/edit_db.html', predator=predator)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)