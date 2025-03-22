""" 
Maneja el control sobre la información de la vista
y los modelos de bases de datos
"""
from models import db, Usuario, Ingreso, Activo, Dinero, PagoReemplazo, PagoHorasExtra, PagoSueldoCliente, RetiroActivo, CatActivo, PagoCotizacionesPrevicionales, Gastos, Option_Client
from flask_login import current_user

class ControladorUsuarios:
    @staticmethod
    def crear_usuario(nombre,apellidos,privilegios,correo,clave):
        usuario = Usuario()
        usuario.nombre = nombre
        usuario.apellidos = apellidos 
        usuario.privilegios = privilegios
        usuario.correo = correo 
        usuario.establecer_clave(clave)
            
        #Agregamos a la base datos
        db.session.add(usuario)
        db.session.commit()
        return usuario

class ControladorDinero:
    @staticmethod
    def dinero(monto_actual):
        dinero = Dinero()
        dinero.monto_actual = monto_actual
        return

class ControladorActivos:
    @staticmethod
    def ingresar_activo(valor, tipo_activo,cantidad, categoria_id):
        activo = Activo(
            valor=valor, 
            tipo_activo=tipo_activo,
            cantidad=cantidad,
            categoria_id=categoria_id
        )

        db.session.add(activo)  
        db.session.commit() 
        return activo
    @staticmethod
    def retirar_activo(id_activo, razon, recibe, cantidad):
        activo = Activo.query.get(id_activo)
        if activo:
            # Resta la cantidad del activo
            if activo.cantidad >= cantidad:
                activo.cantidad -= cantidad 
                if activo.cantidad == 0:
                    activo.retirado = True 

                retiro_activo = RetiroActivo(id_activo=id_activo, razon=razon, recibe=recibe, cantidad=cantidad)
                db.session.add(retiro_activo)
                db.session.commit()

            else:
                raise ValueError("Cantidad insuficiente")

        return activo
    @staticmethod
    def registrar_categoria(categoria):
        categorias = CatActivo(
            categoria=categoria
        )
        db.session.add(categorias)
        db.session.commit()
        return categorias

class ControladorIngreso:
    @staticmethod
    def ingresos(cliente,establecimiento,responsable_pago,num_factura,fecha,medio_pago,monto,descuento,total_descuento,total_utilidad,concepto_pago,motivo_ingreso):
        
        ingreso = Ingreso()
        ingreso.cliente = cliente
        ingreso.establecimiento = establecimiento
        ingreso.responsable_pago = responsable_pago
        ingreso.num_factura = num_factura
        ingreso.fecha = fecha
        ingreso.medio_pago = medio_pago
        ingreso.monto = monto
        ingreso.descuento = descuento
        ingreso.total_descuento = total_descuento
        ingreso.total_utilidad = total_utilidad
        ingreso.concepto_pago = concepto_pago
        ingreso.motivo_ingreso = motivo_ingreso
        ingreso.usuario_id = current_user.id

        db.session.add(ingreso)
        db.session.commit()
        
        return ingreso
    @staticmethod
    def actualizar_ingreso(cliente,establecimiento,responsable_pago,num_factura,fecha,medio_pago,concepto_pago,motivo_ingreso):

        actualizar_ingreso = Ingreso()
        actualizar_ingreso.cliente = cliente
        actualizar_ingreso.establecimiento = establecimiento
        actualizar_ingreso.responsable_pago = responsable_pago
        actualizar_ingreso.num_factura = num_factura
        actualizar_ingreso.fecha = fecha
        actualizar_ingreso.medio_pago = medio_pago
        actualizar_ingreso.concepto_pago = concepto_pago
        actualizar_ingreso.motivo_ingreso = motivo_ingreso

        db.session.add(actualizar_ingreso)
        db.session.commit()
        
        return actualizar_ingreso
    
    def obtener_por_id(id):
        return Ingreso.query.filter(Ingreso.id == id).first()
    
class ControladorEgreso:
    @staticmethod
    def horas_extra(cliente,establecimiento,nombre, rut, dia_trabajado, turno, monto, nombre_paga):
        
        h_extra = PagoHorasExtra()
        h_extra.cliente = cliente
        h_extra.establecimiento = establecimiento
        h_extra.nombre = nombre
        h_extra.rut = rut
        h_extra.dia_trabajado = dia_trabajado
        h_extra.turno = turno
        h_extra.monto = monto
        h_extra.nombre_paga = nombre_paga
        db.session.add(h_extra)
        db.session.commit()
        return h_extra
    @staticmethod
    def pago_reemplazo(nombre, rut, dia_trabajado, turno, monto_pagar, nombre_paga, pago_cotizacion, pago_sueldo):
        try:
            p_reemplazo = PagoReemplazo(
                nombre=nombre,
                rut=rut,
                dia_trabajado=dia_trabajado,
                turno=turno,
                monto_pagar=monto_pagar,
                nombre_paga=nombre_paga,
                pago_cotizacion=pago_cotizacion,
                pago_sueldo=pago_sueldo
            )

            db.session.add(p_reemplazo)
            db.session.commit()
            return p_reemplazo

        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar el pago de reemplazo: {e}")
            return None
    
    @staticmethod
    def pago_sueldo_cliente(cliente, establecimiento, responsable_pago, monto_pagar,factura, nombre, rut, n_cuenta):


        
        p_sueldo = PagoSueldoCliente()
        p_sueldo.cliente = cliente
        p_sueldo.establecimiento = establecimiento
        p_sueldo.responsable_pago = responsable_pago
        p_sueldo.monto = monto_pagar
        p_sueldo.factura = factura
        p_sueldo.nombre = nombre
        p_sueldo.rut = rut
        p_sueldo.numero_cuenta = n_cuenta


        db.session.add(p_sueldo)
        db.session.commit()
        return p_sueldo
    @staticmethod
    def pago_cotizaciones(cliente, establecimiento, responsable_pago, monto_pagar, nombre, rut, fecha_pago):


        
        p_cotizacion = PagoCotizacionesPrevicionales()
        p_cotizacion.cliente = cliente
        p_cotizacion.establecimiento = establecimiento
        p_cotizacion.responsable_pago = responsable_pago
        p_cotizacion.monto = monto_pagar
        p_cotizacion.nombre = nombre
        p_cotizacion.rut = rut
        p_cotizacion.fecha_pago = fecha_pago


        db.session.add(p_cotizacion)
        db.session.commit()
        return p_cotizacion
    
    @staticmethod
    def gasto(motivo_gasto, monto):
        gasto = Gastos(
            motivo_gasto=motivo_gasto,
            monto = monto
        )

        db.session.add(gasto)
        db.session.commit()

        return gasto
    
class ControladorClientes:
    @staticmethod
    def add_cliente(nombre_Cliente):
        clientes = Option_Client(
            nombre_Cliente = nombre_Cliente
        )

        db.session.add(clientes)
        db.session.commit()

        return clientes