"""
    Archivo de modelos de bases de datos
"""
from app import db
from flask_login import UserMixin
from sqlalchemy import func, event
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

#Modelos de bases de datos
class Usuario(db.Model, UserMixin):
    __tablename__  = "usuarios"
    id             = db.Column(db.Integer,primary_key=True)
    nombre         = db.Column(db.String(255),nullable=False)
    apellidos      = db.Column(db.String(255),nullable=True)
    privilegios    = db.Column(db.String(255), nullable=True)
    correo         = db.Column(db.String(255),nullable=True,unique=True)
    clave          = db.Column(db.String(255),nullable=True)

    def establecer_clave(self, clave):
        self.clave = generate_password_hash(clave)
    def chequeo_clave(self, clave):
        return check_password_hash(self.clave, clave)
    @staticmethod
    def obtener_todos():
        all_items = db.session.execute(db.select(Usuario)).scalars()
        all_items_list = []
        for item in all_items:
            all_items_list.append(item)   
        print("Items de consulta:",all_items_list)
        return(all_items_list)     
    @staticmethod 
    def obtener_por_correo(correo):
        usuario = Usuario.query.filter_by(correo=correo).first()
        print(f"Consultando por el usuario {usuario} en db")
        return(usuario)
    @staticmethod
    def obtener_por_id(id):
        print(f"Consultando por el usuario con id{id} en db")
        return Usuario.query.get(id)


class Dinero(db.Model):
    __tablename__       = "dinero"
    id                  = db.Column(db.Integer, primary_key=True)
    monto_actual        = db.Column(db.Integer, nullable=False, default=0)

    dinero_ingreso      = db.relationship("Ingreso", backref='dinero', lazy=True)

    dinero_horas_extra      = db.relationship("PagoHorasExtra", backref='dinero', lazy=True)
    dineroreemplazo         = db.relationship("PagoReemplazo", backref='dinero', lazy=True)
    dinero_sueldos          = db.relationship("PagoSueldoCliente", backref='dinero', lazy=True)

    @staticmethod
    def obtener_por_dinero():
        return Dinero.query.first()


class Ingreso(db.Model):
    __tablename__       = "ingresos"
    id                  = db.Column(db.Integer, primary_key=True)

    cliente             = db.Column(db.String(255), nullable=False)
    establecimiento     = db.Column(db.String(255), nullable=False)
    responsable_pago    = db.Column(db.String(255), nullable=False)
    num_factura         = db.Column(db.String(255), nullable=False)
    dia                 = db.Column(db.String(255), nullable=False)
    mes                 = db.Column(db.String(255), nullable=False)
    año                 = db.Column(db.String(255), nullable=False)
    medio_pago          = db.Column(db.String(255), nullable=False)
    monto               = db.Column(db.Integer, nullable=False, default=0)
    descuento           = db.Column(db.String(255), nullable=False)
    total_descuento     = db.Column(db.Integer, nullable=False, default=0)
    total_utilidad      = db.Column(db.Integer, nullable=False)
    concepto_pago       = db.Column(db.String(255), nullable=False)
    motivo_ingreso      = db.Column(db.Text, nullable=False, default="(En blanco)")
    created_at          = db.Column(db.DateTime, nullable=False, default=func.now())

    dinero_ingreso      = db.Column(db.Integer, db.ForeignKey("dinero.id"))

    @staticmethod
    def obtener_ingresos():
        return Ingreso.query.all()  

class Activo(db.Model):
    __tablename__    = "activos"

    id               = db.Column(db.Integer, primary_key=True)
    categoria        = db.relationship("CatActivo", back_populates="activos")
    valor            = db.Column(db.Integer, nullable=False)
    tipo_activo      = db.Column(db.String(255), nullable=False)
    cantidad         = db.Column(db.Integer, nullable=False)
    retirado         = db.Column(db.Boolean, default=False)
    categoria_id     = db.Column(db.Integer, db.ForeignKey('cat_activo.id'), nullable=False)

    retiro_activo    = db.relationship("RetiroActivo", backref='activos', lazy=True)

    @staticmethod
    def obtener_activos():
        return Activo.query.all()
    
    @staticmethod
    def obtener_activos_retirados():
        return Activo.query.filter_by(retirado=False).all()

    def acumular(self, cantidad_a_sumar):
        
        self.cantidad += cantidad_a_sumar
        db.session.commit()

    @staticmethod
    def acumular_por_categoria(categoria_id, cantidad_a_sumar):
        activos = Activo.query.filter_by(categoria_id=categoria_id).all()
        for activo in activos:
            activo.cantidad += cantidad_a_sumar
        db.session.commit()

    @staticmethod
    def obtener_categorias():
        return CatActivo.query.all()


class CatActivo(db.Model):
    __tablename__       = "cat_activo"

    id                  = db.Column(db.Integer, primary_key=True)
    categoria           = db.Column(db.String(255), nullable=False, unique=True)

    activos             = db.relationship("Activo", back_populates="categoria", lazy=True)


@event.listens_for(Session, "before_delete")
def actualizar_stock_al_eliminar(session, target):
    if isinstance(target, Activo) and target.categoria:
        target.categoria.stock_total -= target.cantidad
        session.commit()

@event.listens_for(Session, "after_update")
def actualizar_stock_al_modificar(session, target):
    if isinstance(target, Activo) and target.categoria:
        target.categoria.actualizar_stock()


class RetiroActivo(db.Model):

    __tablename__    = "r_activo"

    id               = db.Column(db.Integer, primary_key=True)
    razon            = db.Column(db.String(255), nullable=False)
    recibe           = db.Column(db.String(255), nullable=False)
    cantidad         = db.Column(db.Integer, nullable=False)
    
    id_activo        = db.Column(db.Integer, db.ForeignKey("activos.id"))
    activo = db.relationship('Activo', backref='retiros', lazy=True)

    @staticmethod
    def obtener_retirados():
        return RetiroActivo.query.all()

#! TABLAS DE MOVIMIENTO SALARIAL

class PagoHorasExtra(db.Model):

    __tablename__    =  "horas"

    id               = db.Column(db.Integer, primary_key = True)

    nombre           = db.Column(db.String(255), nullable=False)
    rut              = db.Column(db.String(12))
    dia_trabajado    = db.Column(db.Date(), nullable=False)
    turno            = db.Column(db.String(255), nullable=False)
    monto_pagar      = db.Column(db.Integer, nullable=False)
    nombre_paga      = db.Column(db.String(255), nullable=False)

    dinero_horas_extra    = db.Column(db.Integer, db.ForeignKey("dinero.id"), nullable=True)

    @staticmethod
    def obtener_horas_extra():
        return PagoHorasExtra.query.all() 

class PagoReemplazo(db.Model):
    __tablename__    ="reemplazo"

    id               = db.Column(db.Integer, primary_key = True)

    nombre           = db.Column(db.String(255), nullable=False)
    rut              = db.Column(db.String(12))
    dia_trabajado    = db.Column(db.Date(), nullable=False)
    turno            = db.Column(db.String(255), nullable=False)
    monto_pagar      = db.Column(db.Integer, nullable=False)
    nombre_paga      = db.Column(db.String(255), nullable=False)
    pago_cotizacion  = db.Column(db.Integer, nullable=False)
    pago_sueldo      = db.Column(db.Integer, nullable=False) 

    dinero_reemplazo = db.Column(db.Integer, db.ForeignKey("dinero.id"))

    @staticmethod
    def obtener_reemplazo():
        return PagoReemplazo.query.all() 


class PagoSueldoCliente(db.Model):
    __tablename__     = "clientes"

    id               = db.Column(db.Integer, primary_key = True)

    cliente          = db.Column(db.String(255), nullable=False)
    establecimiento  = db.Column(db.String(255), nullable=False)
    responsable_pago = db.Column(db.String(255), nullable=False)
    monto            = db.Column(db.Integer, nullable=False)
    factura          = db.Column(db.LargeBinary, nullable=False)
    nombre           = db.Column(db.String(255), nullable=False)
    rut              = db.Column(db.String(12), nullable=False)
    numero_cuenta    = db.Column(db.String(255), nullable=False)

    dinero_sueldos   = db.Column(db.Integer, db.ForeignKey("dinero.id"))

    @staticmethod
    def obtener_sueldo_cliente():
        return PagoSueldoCliente.query.all() 






