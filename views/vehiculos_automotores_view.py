from flask import render_template

# Listado de todos los vehículos
def list(vehiculos):
    return render_template('vehiculos_automotores/index.html', vehiculos=vehiculos)

# Formulario de creación de nuevo vehículo
def create():
    return render_template('vehiculos_automotores/create.html')

# Formulario de edición de un vehículo específico
def edit(vehiculo):
    return render_template('vehiculos_automotores/edit.html', vehiculo=vehiculo)

#Fromulario de asignacion

