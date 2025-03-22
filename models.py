"""
    Archivo de modelos de bases de datos
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import extract

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
        return(all_items_list)     
    @staticmethod 
    def obtener_por_correo(correo):
        usuario = Usuario.query.filter_by(correo=correo).first()
        return(usuario)
    @staticmethod
    def obtener_por_id(id):
        return Usuario.query.get(id)
    @staticmethod
    def obtener_usuarios():
        return Usuario.query.all()

class Dinero(db.Model):
    __tablename__       = "dinero"
    id                  = db.Column(db.Integer, primary_key=True)
    monto_actual        = db.Column(db.Integer, nullable=False, default=0)

    dinero_ingreso      = db.relationship("Ingreso", backref='dinero', lazy=True)

    dinero_horas_extra      = db.relationship("PagoHorasExtra", backref='dinero', lazy=True)
    dineroreemplazo         = db.relationship("PagoReemplazo", backref='dinero', lazy=True)
    dinero_sueldos          = db.relationship("PagoSueldoCliente", backref='dinero', lazy=True)
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    @staticmethod
    def obtener_egresos_por_tipo(tipo, año):
        egresos = Dinero.query.filter(
            db.extract('year', Dinero.created_at) == año
        ).all()

        if tipo == 'Ingreso':
            return sum(ingreso.monto for ingreso in egresos if ingreso.dinero_ingreso)
        elif tipo == 'Horas Extra':
            return sum(pago.monto for pago in egresos if pago.dinero_horas_extra)
        elif tipo == 'Reemplazo':
            return sum(pago.monto for pago in egresos if pago.dinero_reemplazo)
        elif tipo == 'Sueldos':
            return sum(pago.monto for pago in egresos if pago.dinero_sueldos)
        else:
            return 0

    @staticmethod
    def obtener_dinero_total(año):
        egresos = Dinero.query.filter(
            db.extract('year', Dinero.created_at) == año
        ).all()
        return sum(egreso.monto_actual for egreso in egresos)

    @staticmethod
    def obtener_por_dinero():
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)
            db.session.commit()
        return dinero

class Ingreso(db.Model):
    __tablename__       = "ingresos"
    id                  = db.Column(db.Integer, primary_key=True)
    cliente_relation    = db.relationship("Option_Client", backref="ingresos")
    establecimiento     = db.Column(db.String(255), nullable=False)
    responsable_pago    = db.Column(db.String(255), nullable=False)
    num_factura         = db.Column(db.String(255), nullable=False)
    fecha               = db.Column(db.Date(), nullable=False)
    medio_pago          = db.Column(db.String(255), nullable=False)
    monto               = db.Column(db.Integer, nullable=False, default=0)
    descuento           = db.Column(db.String(255), nullable=False)
    total_descuento     = db.Column(db.Integer, nullable=False, default=0)
    total_utilidad      = db.Column(db.Integer, nullable=False)
    concepto_pago       = db.Column(db.String(255), nullable=False)
    motivo_ingreso      = db.Column(db.Text, nullable=False, default="(En blanco)")
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    cliente             = db.Column(db.Integer, db.ForeignKey("option_clients.id"), nullable=False)
    dinero_ingreso      = db.Column(db.Integer, db.ForeignKey("dinero.id"))

    @staticmethod
    def obtener_ingresos():
        return Ingreso.query.all()  
    
    @staticmethod
    def obtener_ingresos_por_año(año):
        return Ingreso.query.filter(extract('year', Ingreso.fecha) == año).all()

class Activo(db.Model):
    __tablename__    = "activos"

    id               = db.Column(db.Integer, primary_key=True)
    categoria        = db.relationship("CatActivo", back_populates="activos")
    valor            = db.Column(db.Integer, nullable=False)
    tipo_activo      = db.Column(db.String(255), nullable=False)
    cantidad         = db.Column(db.Integer, nullable=False)
    retirado         = db.Column(db.Boolean, default=False)
    categoria_id     = db.Column(db.Integer, db.ForeignKey('cat_activo.id'), nullable=False)
    created_at       = db.Column(db.DateTime, default=db.func.now()) 
    updated_at       = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    retiro_activo    = db.relationship("RetiroActivo", backref='activos', lazy=True, overlaps="activos,retiro_activo")

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
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    activos             = db.relationship("Activo", back_populates="categoria", lazy=True)

class RetiroActivo(db.Model):

    __tablename__    = "r_activo"

    id               = db.Column(db.Integer, primary_key=True)
    razon            = db.Column(db.String(255), nullable=False)
    recibe           = db.Column(db.String(255), nullable=False)
    cantidad         = db.Column(db.Integer, nullable=False)
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 
    
    id_activo        = db.Column(db.Integer, db.ForeignKey("activos.id"))
    activo           = db.relationship('Activo', backref='retiros', lazy=True, overlaps="activos,retiro_activo")

    @staticmethod
    def obtener_retirados():
        return RetiroActivo.query.all()

#! TABLAS DE MOVIMIENTO SALARIAL

class PagoHorasExtra(db.Model):

    __tablename__    =  "horas"

    id               = db.Column(db.Integer, primary_key = True)

    cliente_relation = db.relationship("Option_Client", backref="horas")
    establecimiento  = db.Column(db.String(255), nullable=False)
    nombre           = db.Column(db.String(255), nullable=False)
    rut              = db.Column(db.String(12))
    dia_trabajado    = db.Column(db.Date(), nullable=False)
    turno            = db.Column(db.String(255), nullable=False)
    monto            = db.Column(db.Integer, nullable=False)
    nombre_paga      = db.Column(db.String(255), nullable=False)
    created_at       = db.Column(db.DateTime, default=db.func.now()) 
    updated_at       = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    cliente             = db.Column(db.Integer, db.ForeignKey("option_clients.id"), nullable=False)
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
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    dinero_reemplazo = db.Column(db.Integer, db.ForeignKey("dinero.id"))

    @staticmethod
    def obtener_reemplazo():
        return PagoReemplazo.query.all() 

class PagoSueldoCliente(db.Model):
    __tablename__ = "clientes"

    id               = db.Column(db.Integer, primary_key=True)

    cliente_relation = db.relationship("Option_Client", backref="clientes")
    establecimiento  = db.Column(db.String(255), nullable=False)
    responsable_pago = db.Column(db.String(255), nullable=False)
    monto            = db.Column(db.Integer, nullable=False)
    factura_ruta     = db.Column(db.String(255), nullable=True)  
    factura_nombre   = db.Column(db.String(255), nullable=True)  
    mime_type        = db.Column(db.String(255), nullable=True)   
    nombre           = db.Column(db.String(255), nullable=False)
    rut              = db.Column(db.String(12), nullable=False)
    numero_cuenta    = db.Column(db.String(255), nullable=False)
    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    dinero_sueldos   = db.Column(db.Integer, db.ForeignKey("dinero.id"))
    cliente             = db.Column(db.Integer, db.ForeignKey("option_clients.id"), nullable=False)

    @staticmethod
    def obtener_sueldo_cliente():
        return PagoSueldoCliente.query.all()
    
class PagoCotizacionesPrevicionales(db.Model):
    __tablename__ = "cotizaciones"

    id                  = db.Column(db.Integer, primary_key=True)
    cliente_relation    = db.relationship("Option_Client", backref="cotizaciones") 
    establecimiento     = db.Column(db.String(255), nullable=False)  
    responsable_pago    = db.Column(db.String(255), nullable=False)  
    monto              = db.Column(db.Integer, nullable=False)      
    nombre             = db.Column(db.String(255), nullable=False)  
    rut                = db.Column(db.String(12), nullable=False)   

    fecha_pago         = db.Column(db.Date, nullable=False)          

    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 
    cliente             = db.Column(db.Integer, db.ForeignKey("option_clients.id"), nullable=False)

    @staticmethod
    def obtener_cotizacion():
        return PagoCotizacionesPrevicionales.query.all()
    
class Gastos(db.Model):
    __tablename__       = "gastos"

    id                  = db.Column(db.Integer, primary_key=True)


    motivo_gasto        = db.Column(db.Text, nullable=False, default="(En blanco)")


    monto               = db.Column(db.Integer, nullable=False)

    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    @staticmethod
    def obtener_gasto():
        return Gastos.query.all() 


class Option_Client(db.Model):
    __tablename__       = "option_clients"

    id                  = db.Column(db.Integer, primary_key=True)

    nombre_Cliente      = db.Column(db.String(255), nullable=False)


    created_at         = db.Column(db.DateTime, default=db.func.now()) 
    updated_at         = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now()) 

    def obtener_Clientes():
        return Option_Client.query.all()

