from flask import render_template
from flask_login import current_user

"""def index():
    return render_template("user/index.html")
"""
def login():
    return render_template("user/login.html")

def register():
    return render_template("user/register.html")

def dashboard(user):
    return render_template('usuarios/index.html', user=user)