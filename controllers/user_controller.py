from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user_model import User
from views import user_view
from database import db

user_bp = Blueprint('user',__name__,url_prefix="/")



@user_bp.route("/")
def index():
    return user_view.login()



#Funcion registrar usuario 
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if User.get_by_username(username):
            flash('El nombre de usuario ya existe.', 'danger')
        else:
            new_user = User(name, email, username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario registrado correctamente. Inicia sesión.', 'success')
            return redirect(url_for('user.login'))

    return user_view.register()


#Funcion logear
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)

        if user and user.verify_password(password):
            login_user(user)
        
            #¡flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('vehiculo.index'))
        else:
            flash('Credenciales inválidas', 'danger')

    return user_view.login()




#Funcion cerrar session
@user_bp.route('/dashboard')
@login_required
def dashboard():
    return user_view.dashboard()

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('user.login'))