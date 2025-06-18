from flask import render_template

# Listado de todos los vehículos
def list(edificios):
    return render_template('edificios/index.html', edificios=edificios)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('edificios/create.html')

# Formulario de edición de un vehículo específico
def edit(edificio):
    return render_template('edificios/edit.html', edificio=edificio)