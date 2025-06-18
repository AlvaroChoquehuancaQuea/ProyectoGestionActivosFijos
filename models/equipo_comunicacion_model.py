from database import db
from datetime import date

class Equipo(db.Model):
    __tablename__ = 'equipos'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(30), nullable=False)
    costo_inicial = db.Column(db.Float, nullable=False)
    fecha_incorporacion = db.Column(db.Date, nullable=False)
    valor_residual = db.Column(db.Float, nullable=False)
    años_vida_util = db.Column(db.Integer, nullable=False)
    factor_de_actualizacion = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255))
    cargo = db.Column(db.String(100))
    responsable = db.Column(db.String(100))

    def __init__(self, descripcion, marca, modelo, estado, costo_inicial,
                 fecha_incorporacion, valor_residual, años_vida_util,
                 factor_de_actualizacion, imagen=None, cargo=None, responsable=None):
        self.descripcion = descripcion
        self.marca = marca
        self.modelo = modelo
        self.estado = estado
        self.costo_inicial = costo_inicial
        self.fecha_incorporacion = fecha_incorporacion
        self.valor_residual = valor_residual
        self.años_vida_util = años_vida_util
        self.factor_de_actualizacion = factor_de_actualizacion
        self.imagen = imagen
        self.cargo = cargo
        self.responsable = responsable

    @property
    def costo_actualizado(self):
        return self.costo_inicial * self.factor_de_actualizacion

    @property
    def depreciacion_acumulada(self):
        # Ejemplo simple de cálculo
        años_transcurridos = (date.today() - self.fecha_incorporacion).days / 365
        tasa_anual = (self.costo_actualizado - self.valor_residual) / self.años_vida_util
        depreciacion = min(años_transcurridos * tasa_anual, self.costo_actualizado - self.valor_residual)
        return max(depreciacion, 0)
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
    @property
    
    def valor_neto(self):
        return self.costo_actualizado - self.depreciacion_acumulada
    
    @classmethod
    def get_all(cls):
      return cls.query.all()
  
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
         