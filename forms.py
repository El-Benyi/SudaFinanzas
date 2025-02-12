"""
    Archivo donde se definen los formularios del sistema
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, SelectField, BooleanField,FileField,DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from flask_wtf.file import FileRequired, FileAllowed

class FormularioRegistro(FlaskForm):    
    nombre          = StringField('Nombre', validators=[DataRequired(), Length(min=3)])
    apellidos       = StringField('Apellido paterno y Materno', validators=[DataRequired(), Length(min=3)])
    privilegios     = SelectField('Privilegios de Administrador', choices=[('Privilegios',''),('Permitir', 'Permitir'), ('Denegar', 'Denegar')], validators=[DataRequired()])

    correo          = EmailField('Correo', validators=[DataRequired(), Email()])
    clave           = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('confirmar_clave', message="Las claves deben ser iguales.")])
    confirmar_clave = PasswordField('Confirmar Contraseña', validators=[DataRequired()])
    submit          = SubmitField('Registrar Usuario')
class FormularioActualizarUsuario(FlaskForm):    
    nombre          = StringField('Nombre', validators=[Length(min=3)])
    apellidos       = StringField('Apellido paterno y Materno', validators=[Length(min=3)])
    privilegios     = SelectField('Privilegios de Administrador', choices=[('Privilegios',''),('Permitir', 'Permitir'), ('Denegar', 'Denegar')])

    correo          = EmailField('Correo', validators=[Email()])
    clave           = PasswordField('Contraseña')
    submit          = SubmitField('Actualizar Información del Usuario')

class FormularioAcceso(FlaskForm):    
    correo = EmailField('Correo', validators=[DataRequired(), Email()])
    clave  = PasswordField('Clave', validators=[DataRequired()])    
    submit = SubmitField('Acceder')


class FormularioIngresarFondos(FlaskForm):
    cliente         = SelectField("Clientes", choices=[('Seleccione Cliente',''),('MOP Temuco', 'MOP Temuco'), ('Servicio de Salud Valdivia', 'Servicio de Salud Valdivia'), ('IPS (Instituto Previsión Social)', 'IPS (Instituto Previsión Social)')], validators=[DataRequired()])
    establecimiento = SelectField("Establecimientos", choices=[('Seleccione Establecimiento',''),('Cesamco Las Animas', 'Cesamco Las Animas'), ('Hospital Adulto Mayor', 'Hospital Adulto Mayor'), ('Padre de las Casas', 'Padre de las Casas'), ('IPS Osorno', 'IPS Osorno'), ('IPS Ptp. Montt', 'IPS Ptp. Montt'), ('IPS Ancud', 'IPS Ancud'), ('IPS Castro', 'IPS Castro')], validators=[DataRequired()])
    responsable     = SelectField("Responsable de pago", choices=[('Seleccione tipo de Pago',''),('Cliente', 'Cliente'), ('Factoring', 'Factoring')], validators=[DataRequired()])
    numero_factura  = IntegerField("Ingrese N° de Factura", validators=[DataRequired()])
    dia             = SelectField("Dia", choices=[("Seleccione Dia", ""),("Lunes","Lunes"), ("Martes","Martes"), ("Miercoles","Miercoles"), ("Jueves","Jueves"), ("Viernes","Viernes"), ("Sabado","Sabado"), ("Domingo","Domingo")], validators=[DataRequired()])
    mes             = SelectField("Mes", choices=[("Seleccione Mes", ""),("Enero","Enero"), ("Febrero","Febrero"), ("Marzo","Marzo"), ("Abril","Abril"), ("Mayo","Mayo"), ("Junio","Junio"), ("Julio","Julio"), ("Agosto","Agosto"), ("Septiembre","Septiembre"), ("Octubre","Octubre"), ("Noviembre","Noviembre"), ("Diciembre","Diciembre")], validators=[DataRequired()])
    año             = SelectField("Año", choices=[("Seleccione Año", ""),("2024","2024"),("2025","2025"),("2026","2026"),("2027","2027"),("2028","2028"),("2029","2029"),("2030","2030"),("2031","2031"),("2032","2032"),("2033","2033"),("2034","2034"),("2035","2035")], validators=[DataRequired()])
    medio_pago      = SelectField("Medio de Pago", choices=[("Seleccione Metodo de Pago", ""),("Transferencia","Transferencia"),("Pago Debito","Pago Debito"),("Cheque","Cheque")], validators=[DataRequired()])
    impuesto        = SelectField("Descuento", choices=[("Seleccione porcentaje de Descuento", ""),("0%","0%"),("1%","1%"),("2%","2%"),("3%","3%"),("4%","4%"),("5%","5%"),("6%","6%"),("7%","7%"),("8%","8%"),("9%","9%"),("10%","10%"),("11%","11%"),("12%","12%"),("13%","13%"),("14%","14%"),("15%","15%"),("16%","16%"),("17%","17%"),("18%","18%"),("19%","19%"),("20%","20%")], validators=[DataRequired()])
    concepto_pago   = SelectField("Concepto de Pago", choices=[("Seleccione el Concepto del Pago", ""),("Pago de servicios ","Pago de servicios "),("Pago por reemplazo","Pago por reemplazo"),("Pago pendiente","Pago pendiente"),("Liquidación BBGG","Liquidación BBGG")], validators=[DataRequired()])
    
    
    ingresar_fondos = IntegerField("Ingresar Fondos", validators=[DataRequired()])
    motivo_ingreso  = StringField("Observaciones")

    submit          = SubmitField('Ingresar Fondos')

class FormularioIngresoActivos(FlaskForm):

    categoria_id    = SelectField("Categoria del Activo", choices=[("Seleccione Categoria", "")],validators=[DataRequired()])
    valor           = IntegerField("Valor del activo", validators=[DataRequired()])
    tipo_activo     = SelectField("Tipo de activo", choices=[('Tipo',''),('Tangible', 'Tangible'), ('Intangible', 'Intangible')], validators=[DataRequired()])
    cantidad        = IntegerField("Cantidad de Activos", validators=[DataRequired()])
    
    submit          = SubmitField('Ingresar Activo')

class FormularioCategoria(FlaskForm):

    categoria       = StringField("Ingrese Nombre de la categoria" ,validators=[DataRequired()])

    submit          = SubmitField("Registrar Categoria")

class FormularioRetiroActivos(FlaskForm):

    razon           = StringField("Razon del Retiro", validators=[DataRequired()])
    recibe          = StringField("¿Quien recibe el Activo?", validators=[DataRequired()])
    cantidad        = IntegerField("Cantidad de Activos", validators=[DataRequired()])       

    submit          = SubmitField('Retirar Activo')

class FormularioPagoHoraExtra(FlaskForm):
    cliente         = SelectField("Clientes", choices=[('Seleccione Cliente',''),('MOP Temuco', 'MOP Temuco'), ('Servicio de Salud Valdivia', 'Servicio de Salud Valdivia'), ('IPS (Instituto Previsión Social)', 'IPS (Instituto Previsión Social)')], validators=[DataRequired()])
    establecimiento = SelectField("Establecimientos", choices=[('Seleccione Establecimiento',''),('Cesamco Las Animas', 'Cesamco Las Animas'), ('Hospital Adulto Mayor', 'Hospital Adulto Mayor'), ('Padre de las Casas', 'Padre de las Casas'), ('IPS Osorno', 'IPS Osorno'), ('IPS Ptp. Montt', 'IPS Ptp. Montt'), ('IPS Ancud', 'IPS Ancud'), ('IPS Castro', 'IPS Castro')], validators=[DataRequired()])

    nombre          = StringField("Nombre del Trabajador", validators=[DataRequired()])
    rut             = StringField("Rut del trabajador", validators=[DataRequired(),Length(8, 12), Regexp(r"^\d{7,8}-[0-9kK]$", message="Formato de RUT inválido (Ej: 12345678-9)")])
    dia_trabajado   = DateField("Día trabajado", validators=[DataRequired()], format="%Y-%m-%d")
    turno           = SelectField('Turnos', choices=[('', 'Horario de turno'), ('diurno', 'Diurno (08:00 a 20:00 hrs)'), ('nocturno', 'Nocturno (20:00 a 08:00 hrs)')], validators=[DataRequired()])
    monto           = IntegerField("Monto a Pagar", validators=[DataRequired()])
    quien_paga      = StringField("Nombre de quien paga", validators=[DataRequired()])

    submit          = SubmitField('Confirmar Pago por Horas Extra')


class FormularioPagoReemplazo(FlaskForm):

    nombre          = StringField("Nombre del Trabajador", validators=[DataRequired()])
    rut             = StringField("Rut del trabajador", validators=[DataRequired(),Length(8, 12), Regexp(r"^\d{7,8}-[0-9kK]$", message="Formato de RUT inválido (Ej: 12345678-9)")])
    dia_trabajado   = DateField("Dia trabajado", validators=[DataRequired()], format="%Y-%m-%d")
    turno           = SelectField('Turnos', choices=[('', 'Horario de turno'), ('diurno', 'Diurno (08:00 a 20:00 hrs)'), ('nocturno', 'Nocturno (20:00 a 08:00 hrs)')], validators=[DataRequired()])
    monto_pagar     = IntegerField("Monto a Pagar", validators=[DataRequired()])
    nombre_paga     = StringField("Nombre de quien Paga", validators=[DataRequired()])
    pago_cotizacion = IntegerField("Monto de Cotización", validators=[DataRequired()])
    pago_sueldo     = IntegerField("Monto Sueldo", validators=[DataRequired()])

    submit          = SubmitField('Confirmar Pago por Reemplazo')


class FormularioPagoSueldoCliente(FlaskForm):

    cliente         = SelectField("Clientes", choices=[('Seleccione Cliente',''),('MOP Temuco', 'MOP Temuco'), ('Servicio de Salud Valdivia', 'Servicio de Salud Valdivia'), ('IPS (Instituto Previsión Social)', 'IPS (Instituto Previsión Social)')], validators=[DataRequired()])
    establecimiento = SelectField("Establecimientos", choices=[('Seleccione Establecimiento',''),('Cesamco Las Animas', 'Cesamco Las Animas'), ('Hospital Adulto Mayor', 'Hospital Adulto Mayor'), ('Padre de las Casas', 'Padre de las Casas'), ('IPS Osorno', 'IPS Osorno'), ('IPS Ptp. Montt', 'IPS Ptp. Montt'), ('IPS Ancud', 'IPS Ancud'), ('IPS Castro', 'IPS Castro')], validators=[DataRequired()])
    quien_paga      = StringField("Nombre de quien paga", validators=[DataRequired()])
    monto_pagar     = IntegerField("Monto a Pagar", validators=[DataRequired()])
    factura         = FileField('Factura', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Solo archivos JPG, PNG y PDF son permitidos')])
    nombre          = StringField("Nombre del Trabajador", validators=[DataRequired()])
    rut             = StringField("Rut del trabajador", validators=[DataRequired(),Length(8, 12), Regexp(r"^\d{7,8}-[0-9kK]$", message="Formato de RUT inválido (Ej: 12345678-9)")])
    numero_cuenta   = StringField("N° de Cuenta", validators=[DataRequired()])

    submit          = SubmitField('Confirmar Pago de Sueldo')