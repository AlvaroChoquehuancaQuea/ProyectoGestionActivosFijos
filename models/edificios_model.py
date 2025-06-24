from database import db
from datetime import date
import qrcode
import os
import json
from flask import current_app
class Edificio(db.Model):
    __tablename__ = 'Edificios'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    uso = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(30), nullable=False)
    costo_inicial = db.Column(db.Float, nullable=False)
    fecha_incorporacion = db.Column(db.Date, nullable=False)
    factura = db.Column(db.Float, nullable=False)
    años_vida_util = db.Column(db.Integer, nullable=False)
    factor_de_actualizacion = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255))
    cargo = db.Column(db.String(100))
    responsable = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    

    def __init__(self, descripcion, categoria, uso, estado, costo_inicial,
                 fecha_incorporacion,factura, años_vida_util,
                 factor_de_actualizacion, imagen=None, cargo=None, responsable=None,user_id=None):
        self.descripcion = descripcion
        self.categoria = categoria
        self.uso = uso
        self.estado = estado
        self.costo_inicial = costo_inicial
        self.fecha_incorporacion = fecha_incorporacion
        self.factura = factura
        self.años_vida_util = años_vida_util
        self.factor_de_actualizacion = factor_de_actualizacion
        self.imagen = imagen
        self.cargo = cargo
        self.responsable = responsable
        
        
        self.user_id = user_id # guardar el usuario dueño

    @property
    def costo_actualizado(self):
        return self.costo_inicial * self.factor_de_actualizacion

    @property
    def depreciacion_acumulada(self):
        # Ejemplo simple de cálculo
        #años_transcurridos = (date.today() - self.fecha_incorporacion).days / 365
        #tasa_anual = (self.costo_actualizado - self.factura) / self.años_vida_util
        depreciacion = self.costo_actualizado*(1/self.años_vida_util)
        return max(depreciacion, 0)
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def get_by_id(cls, id_vehiculo):
        return cls.query.filter_by(id=id_vehiculo).first()    
    
    @property
    def valor_neto(self):
        return self.costo_actualizado - self.depreciacion_acumulada
    
    @classmethod
    def get_all(cls):
      return cls.query.all()
  
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        self.generar_qr()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
  
    def generar_qr(self):
        try:
        # Construir el diccionario con los datos del vehículo
            datos_qr = {
                "id": self.id,
                "descripcion": self.descripcion,
                "categoria": self.categoria,
                "uso": self.uso,
                "estado": self.estado,
                "costo_inicial": self.costo_inicial,
                "fecha_incorporacion": self.fecha_incorporacion.strftime('%Y-%m-%d')  # Formato ISO para parsear fácilmente
            }

            # Convertir a JSON
            datos_json = json.dumps(datos_qr)

            # Ruta relativa para guardar el QR
            nombre_archivo = f"edificio_{self.id}.png"
            ruta_relativa = os.path.join('qr', nombre_archivo)
            ruta_absoluta = os.path.join(current_app.root_path, 'static', ruta_relativa)

            # Asegurar que el directorio exista
            os.makedirs(os.path.dirname(ruta_absoluta), exist_ok=True)

            # Crear el QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(datos_json)
            qr.make(fit=True)
            imagen_qr = qr.make_image(fill_color="black", back_color="white")

            # Guardar la imagen
            imagen_qr.save(ruta_absoluta)

            print(f"[QR GENERADO] Ruta: {ruta_absoluta}")
            return True

        except Exception as e:
            print(f"[ERROR QR] No se pudo generar el QR: {str(e)}")
            return False
                  
         