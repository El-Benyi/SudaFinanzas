"""
Archivo app.py: módulo principal de la aplicación.
"""
# Importamos librerias necesarias 
import os
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit


from flask_sqlalchemy import SQLAlchemy #base de datos
from flask_migrate import Migrate #versiones de bases de datos
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy import extract

from werkzeug.security import generate_password_hash


app = Flask(__name__) 

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config["SECRET_KEY"] = "sudcap_finanzas"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root@localhost:3306/suda_finanzas"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app) #iniciamos bases de datos

socketio = SocketIO(app)

login_manager = LoginManager(app) #iniciamos uso de sesiones
login_manager.login_view = "auth"

from forms import FormularioRegistro,FormularioPagoCotizacionesPrevicionales,FormularioActualizarActivo,FormularioRetiroActivos,FormularioActualizarUsuario,FormularioClientes, BuscadorForm, FormularioActualizarIngreso,FormularioAcceso, FormularioIngresarFondos, FormularioPagoHoraExtra, FormularioIngresoActivos, FormularioPagoReemplazo, FormularioPagoSueldoCliente, FormularioCategoria, FormularioGastos
from models import Usuario, Ingreso, PagoCotizacionesPrevicionales, Activo, Dinero, PagoReemplazo, PagoHorasExtra, PagoSueldoCliente, RetiroActivo, CatActivo, Gastos, Option_Client
from controllers import ControladorUsuarios, ControladorActivos, ControladorEgreso, ControladorIngreso, ControladorClientes
from datetime import datetime

Migrate(app,db)


@login_manager.user_loader
def load_user(user_id):
    return Usuario.obtener_por_id(int(user_id))
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/")
def auth(form_registro=None, form_acceso=None):
    if current_user.is_authenticated:
        return redirect("/home")
    
    if form_registro == None:
        form_registro = FormularioRegistro()
    if form_acceso == None: 
        form_acceso = FormularioAcceso()
    return render_template("login.html",form_registro=form_registro,form_acceso=form_acceso)


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    form  = FormularioRegistro()
    error = None 
    usuario = Usuario.obtener_usuarios()

    if current_user.privilegios == "Total": 
    
        if form.validate_on_submit():
            nombre = form.nombre.data
            apellidos = form.apellidos.data
            privilegios = form.privilegios.data
            correo = form.correo.data 
            clave  = form.clave.data 
            
            usuario = Usuario().obtener_por_correo(correo)
            if usuario is not None: # SI EL USUARIO EXISTE SE MANDA UN MENSAJE DE ERROR DICIENDO QUE YA EXISTE
                error = f"El correo {correo} ya se encuentra registrado"
                print(error)
                flash(error)
                return(redirect("/"))
            else: # SI EL USUARIO NO EXISTE SE CREA UN NUEVO USUARIO
                
                ControladorUsuarios().crear_usuario(nombre, apellidos, privilegios, correo, clave)
                        
                return redirect("/home")
        else:
            print("form invalido")
            flash("Form invalido")
            return render_template("register.html", form_registro=form)
    else:
        return redirect(url_for("home"))
        

@app.route("/login", methods=["GET", "POST"])
def login():
    form_acceso = FormularioAcceso()
    if form_acceso.validate_on_submit():
        flash(f"Acceso solicitado para el usuario { form_acceso.correo.data }")
        usuario = Usuario().obtener_por_correo(form_acceso.correo.data)
        if usuario is not None:
            if usuario.chequeo_clave(form_acceso.clave.data):
                login_user(usuario)
                return(redirect("/home"))
            else:
                flash(f"Clave incorrecta")
                print(f"Clave incorrecta")
                return(redirect("/"))
        else:
            flash(f"El usuario no esta registrado")
            print(f"El usuario no esta registrado")
            return(redirect("/"))
    
@app.route("/logout")
def logout():
    logout_user()
    flash(f"El usuario ha cerrado sesión")
    print(f"El usuario ha cerrado sesión")
    return(redirect("/"))


@app.route("/home", methods=["GET"])
@login_required
def home():
    ingresos = Ingreso.query

    filtro_ing_año = request.args.get('filtro_año')
    filtro_ing_mes = request.args.get('filtro_mes')

    if filtro_ing_año:
        ingresos = ingresos.filter(extract("year", Ingreso.fecha) == int(filtro_ing_año))

    if filtro_ing_mes:
        ingresos = ingresos.filter(extract("month", Ingreso.fecha) == int(filtro_ing_mes))

    ingresos = ingresos.all()

    return render_template("index.html", ingresos=ingresos)


@app.route("/ingresos", methods=["GET", "POST"])
@login_required
def ingresar_fondos():
    if current_user.privilegios != "Total":
        return redirect("/")
    
    form = FormularioIngresarFondos()
    dinero_actual = Dinero.obtener_por_dinero()

    clientes = Option_Client.query.all()  
    if not clientes:
        flash("No hay clientes registrados. Agregue un cliente antes de continuar.", "warning")
        return redirect(url_for("agregar_cliente"))

    form.cliente.choices = [(str(cliente.id), cliente.nombre_Cliente) for cliente in clientes]

    if current_user.privilegios == "Total":
        def calcular_descuento(monto, descuento):

            porcentaje_descuento = int(descuento.replace('%', '')) / 100
            return monto * porcentaje_descuento
        def calcular_utilidad(monto, total_descuento):
            return monto - total_descuento

        if form.validate_on_submit():  
            cliente = form.cliente.data
            establecimiento = form.establecimiento.data
            responsable_pago = form.responsable_pago.data
            num_factura = form.num_factura.data
            fecha = form.fecha.data
            medio_pago = form.medio_pago.data
            monto = form.ingresar_fondos.data
            descuento = form.impuesto.data
            total_descuento = calcular_descuento(monto, descuento) 
            total_utilidad = calcular_utilidad(monto, total_descuento)
            concepto_pago = form.concepto_pago.data
            motivo_ingreso = form.motivo_ingreso.data

            ingreso = ControladorIngreso.ingresos(
                cliente, establecimiento, responsable_pago, num_factura,
                fecha, medio_pago, monto, descuento, total_descuento,
                total_utilidad, concepto_pago, motivo_ingreso
            )

            dinero = Dinero.query.first()
            if not dinero:
                dinero = Dinero(monto_actual=0)
                db.session.add(dinero)
            dinero.monto_actual += total_utilidad
            db.session.commit()



            return redirect(url_for("home"))
    else:   
        return redirect(url_for("home"))


    return render_template("ingresos.html", form=form, dinero_actual=dinero_actual)

#! ELIMINAR INGRESOS

@app.route("/eliminar_ingreso/<int:ingreso_id>")
@login_required
def eliminar_ingreso(ingreso_id):
    if current_user.privilegios != "Total":
        return redirect("/")

    ingreso = Ingreso.query.get(ingreso_id)

    db.session.delete(ingreso)
    db.session.commit()


    return redirect("/home")

#* EDITAR INGRESO

@app.route("/editar_ingreso/<int:id>", methods=["GET", "POST"])
@login_required
def editar_ingreso(id):
    if current_user.privilegios != "Total":
        return redirect("/")

    ingreso = Ingreso.query.get(id)
    
    # SI EL USUARIO NO EXISTE REDIRIGE AL PRINCIPIO
    if not ingreso:
        return redirect("/")

    form = FormularioActualizarIngreso(obj=ingreso)

    if form.validate_on_submit():
        # CONDICIONALES PARA VER SI HAY ALGUN CAMBIO EN LA INFORMACION, SI NO HAY CAMBIOS SE MANTIENE LA INFORMACION ANTERIOR

        if form.cliente.data != ingreso.cliente:
            ingreso.cliente = form.cliente.data
        if form.establecimiento.data != ingreso.establecimiento:
            ingreso.establecimiento = form.establecimiento.data
        if form.responsable_pago.data != ingreso.responsable_pago:
            ingreso.responsable_pago = form.responsable_pago.data
        if form.num_factura.data != ingreso.num_factura:
            ingreso.num_factura = form.num_factura.data
        if form.fecha.data != ingreso.fecha:
            ingreso.fecha = form.fecha.data
        if form.medio_pago.data != ingreso.medio_pago:
            ingreso.medio_pago = form.medio_pago.data
        if form.concepto_pago.data != ingreso.concepto_pago:
            ingreso.concepto_pago = form.concepto_pago.data
        if form.motivo_ingreso.data != ingreso.motivo_ingreso:
            ingreso.motivo_ingreso = form.motivo_ingreso.data

        db.session.commit()
        return redirect("/")
    else: 
        print(f"Error al actualizar, {form.errors}")

            
    return render_template("update_ing.html", form=form, ingreso=ingreso)

#? FUNCIONES Y RUTAS DE EGRESO

@app.route("/egresos", methods=["GET", "POST"])
@login_required
def egresos():
    horas = PagoHorasExtra.obtener_horas_extra()
    reemplazos = PagoReemplazo.obtener_reemplazo()
    sueldos = PagoSueldoCliente.obtener_sueldo_cliente()
    cotizaciones = PagoCotizacionesPrevicionales.obtener_cotizacion()
    gastos = Gastos.obtener_gasto()

    return render_template("egresos.html", horas=horas, reemplazos=reemplazos, sueldos=sueldos, cotizaciones=cotizaciones, gastos=gastos)



@app.route("/egresos/pago_horas_extra", methods=["GET", "POST"])
@login_required
def pago_horas_extra():
    if current_user.privilegios != "Total":
        return redirect("/")

    form = FormularioPagoHoraExtra()
    dinero = Dinero.query.first()
    
    clientes = Option_Client.query.all()  
    if not clientes:
        flash("No hay clientes registrados. Agregue un cliente antes de continuar.", "warning")
        return redirect(url_for("agregar_cliente"))

    form.cliente.choices = [(str(cliente.id), cliente.nombre_Cliente) for cliente in clientes]

    if form.validate_on_submit():
        
        try:
            try:
                monto = float(form.monto.data)
            except ValueError:
                flash("Error: El monto ingresado no es válido.", "danger")
                return render_template("horas_extra.html", form=form)

            if dinero and dinero.monto_actual >= monto:
                nuevo_pago_h = ControladorEgreso.horas_extra(
                    cliente=form.cliente.data,
                    establecimiento=form.establecimiento.data,
                    nombre=form.nombre.data,
                    rut=form.rut.data,
                    dia_trabajado=form.dia_trabajado.data,
                    turno=form.turno.data,
                    monto=form.monto.data,
                    nombre_paga=form.quien_paga.data
                )

                # Restar dinero y guardar cambios
                dinero.monto_actual -= monto
                db.session.commit()

                flash("Pago de horas extra registrado correctamente.", "success")
                return redirect(url_for("egresos"))
            else:
                flash("Error: Fondos insuficientes.", "danger")

        except Exception as e:
            flash(f"Error inesperado: {str(e)}", "danger")
            return render_template("horas_extra.html", form=form)

    else:
        flash("Hubo un error en el formulario. Revise los campos.", "danger")

    return render_template("horas_extra.html", form=form)

@app.route("/egresos/pago_reemplazos", methods=["GET", "POST"])
@login_required
def pago_reemplazo():
    if current_user.privilegios != "Total":
        return redirect("/")
    form = FormularioPagoReemplazo()

    if form.validate_on_submit():
        
        nombre = form.nombre.data
        rut = form.rut.data
        dia_trabajado = form.dia_trabajado.data
        turno = form.turno.data
        monto = form.monto_pagar.data
        pagador = form.nombre_paga.data
        pago_cotizacion = form.pago_cotizacion.data
        pago_sueldo = form.pago_sueldo.data

        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)
            db.session.commit()

        if dinero.monto_actual < monto:
            flash('Saldo insuficiente para realizar el pago', 'danger')
            return redirect('/egresos/pago_reemplazos')

        try:
            nuevo_reemplazo = ControladorEgreso.pago_reemplazo(
                nombre, rut, dia_trabajado, turno, monto, pagador, pago_cotizacion, pago_sueldo
            )
            db.session.add(nuevo_reemplazo)

            dinero.monto_actual -= monto
            db.session.commit()
            flash("Pago registrado con éxito", "success")

            return redirect(url_for("egresos"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar el pago: {str(e)}", "danger")

    else:
        flash("Hubo un error en el formulario. Revisa los campos.", "warning")
        print("Errores en el formulario:", form.errors)

    return render_template("reemplazos.html", form=form)

@app.route("/egresos/pago_sueldos", methods=["GET", "POST"])
@login_required
def pago_sueldos():
    if current_user.privilegios != "Total":
        return redirect("/")
    form = FormularioPagoSueldoCliente()

    clientes = Option_Client.query.all()  
    if not clientes:
        flash("No hay clientes registrados. Agregue un cliente antes de continuar.", "warning")
        return redirect(url_for("agregar_cliente"))

    # Llenar el campo SelectField con los clientes
    form.cliente.choices = [(str(cliente.id), cliente.nombre_Cliente) for cliente in clientes]

    if form.validate_on_submit():
        
        cliente = form.cliente.data
        establecimiento = form.establecimiento.data
        responsable_pago = form.quien_paga.data
        monto_pagar = form.monto_pagar.data
        factura = form.factura.data
        nombre = form.nombre.data
        rut = form.rut.data
        n_cuenta = form.numero_cuenta.data

        if factura:
            if allowed_file(factura.filename):
                filename = secure_filename(factura.filename)
                
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, filename)
                factura.save(filepath)

                factura_ruta = filename
                factura_nombre = factura.filename
                mime_type = factura.content_type
            else:
                flash('Tipo de archivo no permitido', 'danger')
                return redirect(url_for('pago_sueldos'))
        else:
            factura_ruta = None
            factura_nombre = None
            mime_type = None

        nuevo_sueldo = PagoSueldoCliente(
            cliente=cliente, 
            establecimiento=establecimiento, 
            responsable_pago=responsable_pago, 
            monto=monto_pagar, 
            factura_ruta=factura_ruta, 
            mime_type=mime_type,
            nombre=nombre, 
            rut=rut, 
            numero_cuenta=n_cuenta
        )
        
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)

        if dinero.monto_actual < monto_pagar:
            flash('Saldo insuficiente para realizar el pago', 'danger')
            return redirect('/egresos/pago_sueldos')

        dinero.monto_actual -= monto_pagar
        db.session.add(nuevo_sueldo)
        db.session.commit()

        return redirect(url_for("egresos"))
    return render_template("sueldos.html", form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)

@app.route("/egresos/pago-cotizaciones", methods=["GET", "POST"])
@login_required
def pago_cotizaciones():
    if current_user.privilegios != "Total":
        return redirect("/")
    form = FormularioPagoCotizacionesPrevicionales()

    clientes = Option_Client.query.all()  
    if not clientes:
        flash("No hay clientes registrados. Agregue un cliente antes de continuar.", "warning")
        return redirect(url_for("agregar_cliente"))

    form.cliente.choices = [(str(cliente.id), cliente.nombre_Cliente) for cliente in clientes]

    if form.validate_on_submit():
        
        cliente = form.cliente.data
        establecimiento = form.establecimiento.data
        responsable_pago = form.quien_paga.data
        monto_pagar = form.monto_pagar.data
        fecha_pago = form.fecha_pago.data
        nombre = form.nombre.data
        rut = form.rut.data

        cotizacion = PagoCotizacionesPrevicionales(
            cliente=cliente, 
            establecimiento=establecimiento, 
            responsable_pago=responsable_pago, 
            monto=monto_pagar,
            nombre=nombre, 
            rut=rut, 
            fecha_pago=fecha_pago
        )
        
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)

        if dinero.monto_actual < monto_pagar:
            flash('Saldo insuficiente para realizar el pago', 'danger')
            return redirect('/egresos/pago-cotizaciones')

        dinero.monto_actual -= monto_pagar
        db.session.add(cotizacion)
        db.session.commit()

        return redirect("/egresos")
    return render_template("cotizaciones.html", form=form)

@app.route("/egresos/gastos", methods=["POST", "GET"])
@login_required
def gastos():
    if current_user.privilegios != "Total":
        return redirect("/")
    
    form = FormularioGastos()

    if form.validate_on_submit():

        motivo_gasto = form.motivo_gasto.data
        monto = form.monto.data

        gasto = ControladorEgreso.gasto(
            motivo_gasto, monto
        )

        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto=0)
            db.session.add(dinero)

        if dinero.monto_actual < monto:
            flash('Saldo insuficiente para completar la operación', 'danger')
            return redirect('/egresos/gastos')
        
        dinero.monto_actual -= monto
        db.session.commit()
        
        return redirect("/egresos")
        
    return render_template("gastos.html", form=form)


#! LOGICA DE ACTIVOS

@app.route("/activos")
@login_required
def index_activos():
    if current_user.privilegios not in ["Permitir", "Total"]:
        return redirect("/")
    activos = Activo.obtener_activos()
    buscador = BuscadorForm() 
    form = FormularioRetiroActivos()

    return render_template("activos.html", activos=activos, form=form, buscador=buscador)

@app.route("/activos/actualizar-activo/<int:id_activo>", methods=["GET", "POST"])
@login_required
def actualizar_activo(id_activo):
    if current_user.privilegios != "Total":
        return redirect("/")
    
    activo = Activo.query.get(id_activo)
    form = FormularioActualizarActivo(obj=activo)
    categorias = Activo.obtener_categorias()
    form.categoria_id.choices = [(categoria.id, categoria.categoria) for categoria in categorias]

    if form.validate_on_submit():
        if form.categoria_id.data != activo.categoria_id:
            activo.categoria_id = form.categoria_id.data

        if form.valor.data != activo.valor:
            activo.valor = form.valor.data

        if form.tipo_activo.data != activo.tipo_activo:
            activo.tipo_activo = form.tipo_activo.data

        if form.cantidad.data != activo.cantidad:
            activo.cantidad = form.cantidad.data
        
        db.session.commit()

        return redirect(url_for('index_activos'))


    return render_template("activos_update.html", form=form)

@app.route("/activos/registrar-activos", methods=["GET", "POST"])
@login_required
def activos():
    if current_user.privilegios != "Total":
        return redirect("/")
    form = FormularioIngresoActivos()

    categorias = Activo.obtener_categorias()

    form.categoria_id.choices = [(categoria.id, categoria.categoria) for categoria in categorias]

    if form.validate_on_submit():
        categoria_id = form.categoria_id.data
        valor = form.valor.data
        tipo_activo = form.tipo_activo.data
        cantidad = form.cantidad.data

        # Verificar si ya existe un activo en la misma categoría
        activo_existente = Activo.query.filter_by(categoria_id=categoria_id).first()

        if activo_existente:
            # Si existe, acumular la cantidad por categoría
            Activo.acumular_por_categoria(categoria_id, cantidad)
        else:
            # Si no existe, crear un nuevo activo
            activo = Activo(
                categoria_id=categoria_id, 
                valor=valor, 
                tipo_activo=tipo_activo, 
                cantidad=cantidad
            )
            db.session.add(activo)

        db.session.commit()
        return redirect(url_for("index_activos"))

    return render_template("registrar_activo.html", form=form)

@app.route("/activos/registrar-categoria", methods=["GET", "POST"])
@login_required
def categoria():
    if current_user.privilegios != "Total":
        return redirect("/")
    
    form = FormularioCategoria()

    if form.validate_on_submit():
        categoria = form.categoria.data

        categorias = ControladorActivos.registrar_categoria(
            categoria = categoria
        )
        db.session.commit()
        return redirect("/activos/registrar-categoria")

    return render_template("cat_register.html", form=form)

@app.route("/activos/buscar", methods=["POST"])
def buscar_activos():
    
    if current_user.privilegios not in ["Permitir", "Total"]:
        return redirect("/")
    
    buscador = BuscadorForm()
    form = FormularioRetiroActivos()  
    if buscador.validate_on_submit():
        busqueda = buscador.buscador.data
        resultado = Activo.query.filter(Activo.categoria.has(CatActivo.categoria.ilike(f"%{busqueda}%"))).all()
        return render_template("activos.html", resultado=resultado, buscador=buscador, form=form)
    return redirect(url_for('index_activos')) 

@app.route("/activos/activos-retirados")
@login_required
def activos_retirados():
    activos = Activo.obtener_activos_retirados()  # Obtiene los activos retirados
    retiros = RetiroActivo.obtener_retirados()  # Obtiene los retiros

    return render_template("activos_retirados.html", activos=activos, retiros=retiros)

@app.route("/activos/retiro-activo/<int:id_activo>", methods=["GET", "POST"])
@login_required
def retiro_activo(id_activo):
    if current_user.privilegios != "Total":
        return redirect("/")
    form = FormularioRetiroActivos()
    buscador = BuscadorForm()

    

    cantidad_stock = Activo.query.get(id_activo).cantidad

    
    if form.validate_on_submit():
        razon = form.razon.data
        recibe = form.recibe.data
        cantidad = form.cantidad.data

        if cantidad > cantidad_stock:
            session[f"flash_message_{id_activo}"] = "Cantidad insuficiente"
            session[f"flash_category_{id_activo}"] = "danger"

            return redirect("/activos")

        try:
            ControladorActivos.retirar_activo(id_activo, razon, recibe, cantidad)
            flash("Operación exitosa", "success")
        except ValueError as e:
            flash(str(e), "danger") 
            return redirect(url_for("index_activos")) 

        return redirect(url_for("index_activos"))

    return render_template("activos.html", form=form, buscador=buscador)

@app.route("/reportes")
@login_required
def reportes():
    año = request.args.get('año', default=datetime.now().year, type=int)

    ingresos_año = Ingreso.obtener_ingresos_por_año(año)

    total_ingresos = sum(ingreso.monto for ingreso in ingresos_año)

    total_horas_extra = sum(hora.monto for hora in PagoHorasExtra.query.filter(PagoHorasExtra.dia_trabajado.between(f"{año}-01-01", f"{año}-12-31")).all())
    total_reemplazo = sum(reemplazo.monto_pagar for reemplazo in PagoReemplazo.query.filter(PagoReemplazo.dia_trabajado.between(f"{año}-01-01", f"{año}-12-31")).all())
    total_sueldos = sum(sueldo.monto for sueldo in PagoSueldoCliente.query.filter(PagoSueldoCliente.created_at.between(f"{año}-01-01", f"{año}-12-31")).all())
    total_cotizaciones = sum(cotizacion.monto for cotizacion in PagoCotizacionesPrevicionales.query.filter(PagoCotizacionesPrevicionales.fecha_pago.between(f"{año}-01-01", f"{año}-12-31")).all())
    total_gastos = sum(gasto.monto for gasto in Gastos.query.filter(Gastos.created_at.between(f"{año}-01-01", f"{año}-12-31")).all())

    # Sumar todos los egresos
    total_egresos = total_horas_extra + total_reemplazo + total_sueldos + total_cotizaciones + total_gastos

    beneficios = total_ingresos - total_egresos 

    

    current_year = datetime.now().year

    return render_template("reportes.html", ingresos=ingresos_año, total_egresos=total_egresos, total_ingresos=total_ingresos, año=año, current_year=current_year, beneficios=beneficios)

@app.route("/administracion")
@login_required
def admin():
    if current_user.privilegios not in ["Permitir", "Total"]:
        return redirect("/")
    user = Usuario.obtener_todos()

    return render_template("administracion.html", user=user)

@app.route("/administracion/editar_usuario/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def editar_usuario(usuario_id):
    if current_user.privilegios != "Total":
        return redirect("/")

    usuario = Usuario.query.get(usuario_id)
    
    # SI EL USUARIO NO EXISTE REDIRIGE AL PRINCIPIO
    if not usuario:
        return redirect("/")

    form = FormularioActualizarUsuario(obj=usuario)

    if form.validate_on_submit():
        # CONDICIONALES PARA VER SI HAY ALGUN CAMBIO EN LA INFORMACION, SI NO HAY CAMBIOS SE MANTIENE LA INFORMACION ANTERIOR

        if form.nombre.data != usuario.nombre:
            usuario.nombre = form.nombre.data

        if form.apellidos.data != usuario.apellidos:
            usuario.apellidos = form.apellidos.data

        if form.privilegios.data != usuario.privilegios:
            usuario.privilegios = form.privilegios.data

        if form.correo.data != usuario.correo:
            usuario.correo = form.correo.data

        if form.clave.data:
            usuario.clave = generate_password_hash(form.clave.data)

        db.session.commit()

        return redirect(url_for('admin'))  

    return render_template("actualizar.html", form=form, usuario=usuario)

@app.route("/eliminar_usuario/<int:id_usuario>", methods=["POST"])
@login_required
def eliminar_usuario(id_usuario):
    if current_user.privilegios != "Total":
        return redirect("/")

    usuario = Usuario.query.get(id_usuario)

    if usuario is None:
        return redirect("/")

    db.session.delete(usuario)
    db.session.commit()

    return redirect("/administracion")

@app.route("/nuevo-cliente", methods=["GET", "POST"])
@login_required
def add_cliente():
    if current_user.privilegios not in ["Total"]:
        return redirect("/")
    
    form = FormularioClientes()

    if form.validate_on_submit():
        nombre_Cliente = form.nombre_Cliente.data

        ControladorClientes.add_cliente(nombre_Cliente)

        return redirect("/")  

    return render_template("Clientes.html", form=form)

@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if current_user.privilegios != "Total":
        return redirect("/")
    

    clientes = Option_Client.obtener_Clientes() 

    return render_template("admin_clientes.html", clientes=clientes)