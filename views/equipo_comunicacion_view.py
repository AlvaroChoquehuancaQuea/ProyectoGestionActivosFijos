from flask import render_template

# Listado de todos los vehículos
def list(equipos):
    return render_template('equipo_comunicacion/index.html', equipos=equipos)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('equipo_comunicacion/create.html')

# Formulario de edición de un vehículo específico
def edit(equipo):
    return render_template('equipo_comunicacion/edit.html', equipo=equipo)