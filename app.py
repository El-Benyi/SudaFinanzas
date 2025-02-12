"""
Archivo app.py: módulo principal de la aplicación.
"""
# Importamos librerias necesarias 
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_socketio import SocketIO, emit

from flask_sqlalchemy import SQLAlchemy #base de datos
from flask_migrate import Migrate #versiones de bases de datos
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from werkzeug.security import generate_password_hash


app = Flask(__name__) 
app.config["SECRET_KEY"] = "sudcap_finanzas"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root@localhost:3306/suda_finanzas"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app) #iniciamos bases de datos

socketio = SocketIO(app)

login_manager = LoginManager(app) #iniciamos uso de sesiones
login_manager.login_view = "auth"

from forms import FormularioRegistro,FormularioRetiroActivos,FormularioActualizarUsuario, FormularioAcceso, FormularioIngresarFondos, FormularioPagoHoraExtra, FormularioIngresoActivos, FormularioPagoReemplazo, FormularioPagoSueldoCliente, FormularioCategoria
from models import Usuario, Ingreso, Activo, Dinero, PagoReemplazo, PagoHorasExtra, PagoSueldoCliente, RetiroActivo, CatActivo
from controllers import ControladorUsuarios, ControladorActivos, ControladorEgreso, ControladorIngreso


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

@socketio.on('connect')
def handle_connect():
    print('Conexión WebSocket exitosa')


@app.route("/home", methods=["GET"])
@login_required
def home():
    ingresos = Ingreso.obtener_ingresos()
    horas = PagoHorasExtra.obtener_horas_extra()
    reemplazos = PagoReemplazo.obtener_reemplazo()
    sueldos = PagoSueldoCliente.obtener_sueldo_cliente()

    filtro_ing_año = request.args.get('filtro_año')

    if filtro_ing_año:
        ingresos = Ingreso.query.filter_by(año=int(filtro_ing_año)).all()
    else:
        ingresos = Ingreso.query.all()


    return render_template("index.html", ingresos=ingresos, horas=horas, reemplazos=reemplazos, sueldos=sueldos)


@app.route("/ingresos", methods=["GET", "POST"])
@login_required
def ingresar_fondos():
    form = FormularioIngresarFondos()
    dinero_actual = Dinero.obtener_por_dinero()
    def calcular_descuento(monto, descuento):

        porcentaje_descuento = int(descuento.replace('%', '')) / 100
        return monto * porcentaje_descuento
    def calcular_utilidad(monto, total_descuento):
        return monto - total_descuento

    if form.validate_on_submit():  
        # Obtenemos los datos del formulario
        cliente = form.cliente.data
        establecimiento = form.establecimiento.data
        responsable_pago = form.responsable.data
        num_factura = form.numero_factura.data
        dia = form.dia.data
        mes = form.mes.data
        año = form.año.data
        medio_pago = form.medio_pago.data
        monto = form.ingresar_fondos.data
        descuento = form.impuesto.data
        total_descuento = calcular_descuento(monto, descuento) 
        total_utilidad = calcular_utilidad(monto, total_descuento)
        concepto_pago = form.concepto_pago.data
        motivo_ingreso = form.motivo_ingreso.data

        ingreso = ControladorIngreso.ingresos(
            cliente, establecimiento, responsable_pago, num_factura,
            dia, mes, año, medio_pago, monto, descuento, total_descuento,
            total_utilidad, concepto_pago, motivo_ingreso
        )

        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)
        dinero.monto_actual += total_utilidad
        db.session.commit()



        return redirect(url_for("home"))

    return render_template("ingresos.html", form=form, dinero_actual=dinero_actual)


#* EDITAR INGRESO

@app.route("/editar_ingreso/<int:id>", methods=["GET", "POST"])
@login_required
def editar_ingreso():
    return 


#? FUNCIONES Y RUTAS DE EGRESO

@app.route("/egresos", methods=["GET", "POST"])
@login_required
def egresos():
    return render_template("egresos.html")

@app.route("/pago_horas_extra", methods=["GET", "POST"])
@login_required
def pago_horas_extra():
    form = FormularioPagoHoraExtra()

    if form.validate_on_submit():
        nombre = form.nombre.data
        rut = form.rut.data
        dia_trabajado = form.dia_trabajado.data
        turno = form.turno.data
        monto = form.monto.data
        pagador = form.quien_paga.data

        nuevo_pago_h = ControladorEgreso.horas_extra(
            nombre, rut, dia_trabajado, turno, monto, pagador
        )
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)

        dinero.monto_actual -= monto
        db.session.commit()

        return redirect(url_for("home"))
    else:
        print("Hubo un error y no se guardaron los datos")
        print("Errores en el formulario:", form.errors)

    return render_template("horas_extra.html", form=form)

@app.route("/pago_reemplazos", methods=["GET", "POST"])
@login_required
def pago_reemplazo():
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

        nuevo_reemplazo = ControladorEgreso.pago_reemplazo(
            nombre , rut , dia_trabajado, turno, monto, pagador, pago_cotizacion, pago_sueldo
        )
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)

        dinero.monto_actual -= monto
        db.session.commit()

        return redirect(url_for("home"))
    else:
        print("Hubo un error y no se guardaron los datos")
        print("Errores en el formulario:", form.errors)

    return render_template("reemplazos.html", form = form)

@app.route("/pago_sueldos", methods=["GET", "POST"])
@login_required
def pago_sueldos():
    form = FormularioPagoSueldoCliente()

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
            factura_binaria = factura.read()  # TRANSFORMA FACTURA A UN TIPO DE DATO QUE LA DB PUEDA LEER
        else:
            factura_binaria = None  

        nuevo_sueldo = ControladorEgreso.pago_sueldo_cliente(
            cliente, establecimiento, responsable_pago, monto_pagar,factura_binaria, nombre, rut, n_cuenta
        )
        dinero = Dinero.query.first()
        if not dinero:
            dinero = Dinero(monto_actual=0)
            db.session.add(dinero)

        dinero.monto_actual -= monto_pagar
        db.session.commit()

        return redirect(url_for("home"))
    else:
        print("Hubo un error y no se guardaron los datos")
        print("Errores en el formulario:", form.errors)

    return render_template("sueldos.html", form=form)




#! LOGICA DE ACTIVOS
@app.route("/registrar-activos", methods=["GET", "POST"])
@login_required
def activos():
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
        return redirect(url_for("home"))

    return render_template("registrar_activo.html", form=form)

@app.route("/registrar-categoria", methods=["GET", "POST"])
@login_required
def categoria():
    form = FormularioCategoria()

    if form.validate_on_submit():
        categoria = form.categoria.data

        categorias = ControladorActivos.registrar_categoria(
            categoria = categoria
        )
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("cat_register.html", form=form)


@app.route("/activos")
@login_required
def index_activos():
    activos = Activo.obtener_activos()
    form = FormularioRetiroActivos()

    return render_template("activos.html", activos=activos, form=form)


@app.route("/activos-retirados")
@login_required
def activos_retirados():
    activos = Activo.obtener_activos_retirados()  # Obtiene los activos retirados
    retiros = RetiroActivo.obtener_retirados()  # Obtiene los retiros

    return render_template("activos_retirados.html", activos=activos, retiros=retiros)


@app.route("/retiro-activo/<int:id_activo>", methods=["GET", "POST"])
@login_required
def retiro_activo(id_activo):
    form = FormularioRetiroActivos()

    if form.validate_on_submit():
        razon = form.razon.data
        recibe = form.recibe.data
        cantidad = form.cantidad.data

        try:
            ControladorActivos.retirar_activo(id_activo, razon, recibe, cantidad)
        except ValueError as e:
            flash(str(e), "danger") 
            return redirect(url_for("index_activos")) 

        return redirect(url_for("home"))

    return render_template("activos.html", form=form)


@app.route("/reportes")
@login_required
def reportes():

    return render_template("reportes.html")
@app.route("/configuracion")
@login_required
def config():
    
    return render_template("configuracion.html")

@app.route("/editar_usuario/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def editar_usuario(usuario_id):
    if current_user.privilegios != "Permitir":
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

        return redirect(url_for('home'))  

    return render_template("actualizar.html", form=form, usuario=usuario)

@app.route("/eliminar_usuario/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def eliminar_usuario(usuario_id):

    usuario_delete = Usuario.query.get_or_404(usuario_id)

    db.session.delete(usuario_delete)
    db.session.commit()

    return redirect("/administracion")

@app.route("/administracion")
@login_required
def admin():
    user = Usuario.obtener_todos()

    return render_template("administracion.html", user=user)