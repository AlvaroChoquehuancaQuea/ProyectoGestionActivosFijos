from flask import Flask,request,render_template,url_for,make_response,redirect
from flask_login import LoginManager
from controllers import edificios_controller
from controllers import equipo_recreativo_controller
from controllers import vehiculos_automotores_controller
from controllers import muebles_enseres_controller
from controllers import equipos_computacion_controller
from controllers import user_controller
from models.user_model import User
from database import db 

from flask import request
from datetime import timedelta

app= Flask(__name__)
app.secret_key = 'clave-secreta'
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///RevalorizadorActivosFijos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Ruta donde se guardarán las imágenes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB para archivos

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.init_app(app)

import os
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    
    
app.register_blueprint(edificios_controller.edificio_bp)
app.register_blueprint(equipo_recreativo_controller.recreativo_bp)
app.register_blueprint(equipos_computacion_controller.computadora_bp)
app.register_blueprint(muebles_enseres_controller.mueble_bp)
app.register_blueprint(vehiculos_automotores_controller.vehiculo_bp)
app.register_blueprint(user_controller.user_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@app.context_processor
def utility_functions():
    def is_active(path):
        return 'active' if request.path.startswith(path) else ''
    return dict(is_active=is_active)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
 