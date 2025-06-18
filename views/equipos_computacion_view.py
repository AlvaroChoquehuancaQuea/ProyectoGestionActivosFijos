from flask import render_template

# Listado de todos los vehículos
def list(computadoras):
    return render_template('equipos_computacion/index.html', computadoras=computadoras)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('equipos_computacion/create.html')

# Formulario de edición de un vehículo específico
def edit(computadora):
    return render_template('equipos_computacion/edit.html', computadora=computadora)