from flask import render_template

# Listado de todos los vehículos
def list(recreativos):
    return render_template('equipo_recreativo/index.html', recreativos=recreativos)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('equipo_recreativo/create.html')

# Formulario de edición de un vehículo específico
def edit(recreativo):
    return render_template('equipo_recreativo/edit.html', recreativo=recreativo)