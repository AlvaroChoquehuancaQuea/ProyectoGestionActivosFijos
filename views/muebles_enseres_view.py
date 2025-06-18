from flask import render_template

# Listado de todos los vehículos
def list(muebles):
    return render_template('muebles_enseres/index.html', muebles=muebles)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('muebles_enseres/create.html')

# Formulario de edición de un vehículo específico
def edit(mueble):
    return render_template('muebles_enseres/edit.html', mueble=mueble)