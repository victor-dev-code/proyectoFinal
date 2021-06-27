
from django.template import Template, Context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import os, html, re, string, requests, base64, sys, datetime
from pagina1 import models
from pagina1.models import Credenciales, Usuarios
from .utils import generar_hash, convertir_cadena_para_almacenar, validar_password, convertir_almacenado_a_original, validar_usuario, validar_password_almacenado
from .cifrar_aes import generar_llave_aes_from_password, cifrar, descifrar
from .generarLlaves import generar_llave_privada, generar_llave_publica, convertir_llave_privada_bytes, convertir_llave_publica_bytes, convertir_bytes_llave_privada, convertir_bytes_llave_publica
from GestionClaves.decoradores import login_requerido, login_requerido2
from datetime import timezone
import string
import random
import logging, platform

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO,
                    filename='resgistros.log', filemode='a')

'''Manda mensaje bot telegram con el token para ingresar a la cuenta, también lo almacena en 
   la base de datos'''
def mandar_mensaje_al_bot(request):
    nick = request.session.get('usuario', 'anonimo')
    datos_almacenados = models.Usuarios.objects.get(nick=nick)
    chat_id = datos_almacenados.chatID
    token = datos_almacenados.tokenT
    mensaje = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    mensaje_enviado = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + mensaje
    requests.get(mensaje_enviado)
    models.Usuarios()
    models.Usuarios.objects.filter(nick=nick).update(tokenEnviado=mensaje, tokenTem=datetime.datetime.now())

''' Se obtiene la ip del cliente que esta tratando de ingresar al sistema '''
def obtener_ip_cliente(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_obtenida = x_forwarded_for.split(',')[0]
    else:
        ip_obtenida = request.META.get('REMOTE_ADDR')
    return ip_obtenida

''' Se recupera el tiempo actual (en segundos) para poder hacer la diferencia
    entre la hora almacenada y la actual'''
def restar_tiempo_actual_y_almacenado(tiempo_almacenado):
    tiempo_actual =  datetime.datetime.now(timezone.utc)
    diferencia = tiempo_actual - tiempo_almacenado
    return diferencia.seconds
    
def comparar_tiempo(ip_cliente):
	 pass
    
def verificar_numero_de_intentos(ip_cliente):
	 pass
	 
    
''' intento de las ip del cliente '''
def intento_ip(ip):
    guardar_registro = models.IntentosIP.objects.filter(pk=ip)
    if not guardar_registro:
        registro = models.IntentosIP(ip=ip, cont=1, last_Peticion=datetime.datetime.now())
        registro.save()
        return True
    guardar_registro = guardar_registro[0]
    diferencia_tiempo = restar_tiempo_actual_y_almacenado(guardar_registro.last_Peticion)
    if diferencia_tiempo > 60:
        guardar_registro.last_Peticion = datetime.datetime.now()
        guardar_registro.cont = 1
        guardar_registro.save()
        return True
    else:
        if guardar_registro.cont < 2:
             guardar_registro.last_Peticion = datetime.datetime.now()
             guardar_registro.cont += 1
             guardar_registro.save()
             return True
        else:
            guardar_registro.last_Peticion = datetime.datetime.now()
            return False

''' Página del token, almacena el token y verifica si ha expirado o si es correcto '''
@login_requerido
def token(request):
    template = 'token.html'
    nick = request.session.get('usuario', 'anonimo')
    if request.method == 'GET':
        return render(request, template)
    elif request.method == 'POST':
        ip_cliente = obtener_ip_cliente(request)
        if intento_ip(ip_cliente):
            token = request.POST.get('token', '').strip()
            try:
                token_almacenado = models.Usuarios.objects.get(tokenEnviado=token)
                if (restar_tiempo_actual_y_almacenado(token_almacenado.tokenTem) > 180):  
                    errores={'El token ha expirado'}
                    return render(request,template,{'errores':errores})
                request.session['logueado2'] = True
                request.session['usuario'] = nick
                logging.info("usuario logueado:" + nick)
                return redirect('/pagina')
            except:
                errores = ['token incorrecto']
                return render(request, "login.html", {'errores': errores})
        else:
            return HttpResponse("Agotaste tus intentos espera 1 minuto") 


'''login de usuario '''
def login(request):
    template = 'login.html'
    if request.method == 'GET':
        logueado = request.session.get('logueado', False)
        if logueado:
            return redirect('/pagina')
        return render(request, template)
    elif request.method == 'POST':
        ip = obtener_ip_cliente(request)
        if intento_ip(ip):
            nick = request.POST.get('nick', '').strip()
            password = request.POST.get('contraseña', '').strip()
            nick = html.escape(nick)
            password = html.escape(password)  
            password = validar_password(password)
            try:
                models.Usuarios.objects.get(nick=nick, password=password)
                request.session['logueado'] = True
                request.session['usuario'] = nick
                '''envia mensaje a telegram despues de pasar el login'''
                mandar_mensaje_al_bot(request)
                return redirect('/token')
            except:
                errores = ['credenciales de usuario o nick incorrectos']    
                return render(request, template, {'errores': errores})
        else:
             return HttpResponse("Agotaste tus intentos espera 1 minuto")
  
'''
registrar usuarios
'''
def escapar_caracteres_especiales(lista_datos):
    resultado = []
    for elemento in lista_datos:
        contenido = html.escape(elemento)
        caracteres_especiales = re.escape(string.punctuation)
        campo = re.sub(r'['+caracteres_especiales+']', '', contenido)
        resultado.append(campo)
    return resultado

def formato_correcto_password(password):
    errores_password = []
    if ' ' in password:
        errores_password.append('La contraseña no debe contener espacios')
    if len(password) < 10:
        errores_password.append('La contraseña debe contener al menos 10 caracteres')
    if not any(caracter.isupper() for caracter in password):
        errores_password.append('La contraseña al menos debe contener una letra mayúscula')
    if not any(caracter.islower() for caracter in password):
        errores_password.append('La contraseña al menos debe contener una letra minúscula')
    if not any(caracter.isdigit() for caracter in password):
        errores_password.append('La contraseña al menos debe contener un número')
    return errores_password

def nick_repetido(usuarios):
    nick = models.Usuarios.objects.filter(nick=usuarios.nick)
    if len(nick) > 0:
        return True
    return False

def correo_repetido(usuarios):
    correo = models.Usuarios.objects.filter(correo=usuarios.correo)
    if len(correo) > 0:
        return True
    return False

def chat_id_repetido(usuarios):
    chatID = models.Usuarios.objects.filter(chatID=usuarios.chatID)
    if len(chatID) > 0:
        return True
    return False

def token_repetido(usuarios):
    tokenT = models.Usuarios.objects.filter(tokenT=usuarios.tokenT) 
    if len(tokenT) > 0:
        return True
    return False 

'''recoleccion de errores'''
def recolectar_errores_registro(usuarios, confirmacion, password):
    errores = []
    expresion_regular_email = re.compile(r'^[a-zA-Z0-9_\-\.~]{2,}@[a-zA-Z0-9_\-\.~]{2,}\.[a-zA-Z]{2,4}$')
    expresion_regular_token_telegram = re.compile(r'^[0-9]{10}:[a-zA-Z0-9_-]{35}$')
    if usuarios.nombre == '':
        errores.append('El campo nombre completo está vacío')
    if len(usuarios.nombre) < 15:
        errores.append('El campo nombre completo debe contener al menos 15 caracteres')
    if usuarios.nick == '':
        errores.append('El campo nick del usuario está vacío')
    if nick_repetido(usuarios):
        errores.append('El nick %s ya existe' % usuarios.nick)
    if len(usuarios.nick) < 5:
        errores.append('El nick debe contener al menos 5 caracteres')
    if usuarios.password == '':
        errores.append('La contraseña está vacía')
    if confirmacion == '':
        errores.append('El campo de confirmación de la contraseña está vacío')
    if not usuarios.password == confirmacion:
        errores.append('La contraseña y su confirmación no coinciden')
    if usuarios.correo == '':
        errores.append('El campo correo está vacío')
    if correo_repetido(usuarios):
        errores.append('El correo %s ya está siendo usado por otro usuario' % usuarios.correo)
    if not expresion_regular_email.match(usuarios.correo):
        errores.append('El correo que ingresó no tiene el formato correcto')
    if usuarios.chatID== '':
        errores.append('el campo del chat id esta vacio')
    if chat_id_repetido(usuarios):
        errores.append('el chat id %s ya esta en uso' % usuarios.chatID)
    if usuarios.tokenT== '':
        errores.append('el campo del token esta vacio')
    if token_repetido(usuarios):
        errores.append('El token %s ya esta en uso' % usuarios.tokenT)
    if len(usuarios.tokenT) < 46:
        errores.append('el token no puede ser menos de 46 caracteres ni mas de 46')
    if not expresion_regular_token_telegram.match(usuarios.tokenT):
        errores.append('el token que ingreso no tiene el formato correcto') 
 
    errores_password = formato_correcto_password(password)
    errores += errores_password
    return errores

'''
formulario de registro
'''
def formulario_registro(request):
    template = 'formulario.html'
    if request.method == 'GET':
        return render(request, template)
    elif request.method == 'POST':
        ip = obtener_ip_cliente(request)
        if intento_ip(ip):
            '''Recuperacion de datos ingresados desde la pagina'''
            nombre = request.POST.get('nomCompleto', '').strip()
            nick = request.POST.get('nick', '').strip()
            password = request.POST.get('contraseña', '').strip()
            confirmacion = request.POST.get('confirmacion', '').strip()
            correo = request.POST.get('email', '').strip()
            chat_id = request.POST.get('chat', '').strip()
            token_telegram = request.POST.get('tokt', '').strip()

            '''Elimina caracteres especiales y verifica el password, correo, token de telegram y chat_id'''
            lista_datos = [nombre, nick, password, confirmacion]
            lista = escapar_caracteres_especiales(lista_datos)

            password = html.escape(password)
            confirmacion = html.escape(confirmacion)
            correo = html.escape(correo)
            chat_id = html.escape(chat_id)
            token_telegram = html.escape(token_telegram)

            '''Creación y proceso de hasheo de contraseña a partir de un archivo externo (utils)'''
            salt = os.urandom(16)
            password_hasheado = generar_hash(password, salt)
            password_confirmacion_hasheado = generar_hash(confirmacion, salt)
            salt_almacenado = convertir_cadena_para_almacenar(salt)

            '''creación de llaves y transforlas a formato PEM (otras cosas)'''
            llave_privada = generar_llave_privada()
            llave_publica = generar_llave_publica(llave_privada)
            llave_privada_pem = convertir_llave_privada_bytes(llave_privada)
            llave_publica_pem = convertir_llave_publica_bytes(llave_publica)
            llave_publica = convertir_cadena_para_almacenar(llave_publica_pem)

            '''Proceso de cifrado de la llave privada'''
            iv = os.urandom(16)
            llave_aes = generar_llave_aes_from_password(password)
            llave_privada_cifrada = cifrar(llave_privada_pem, llave_aes, iv)
            llave_privada = convertir_cadena_para_almacenar(llave_privada_cifrada)
            iv_almacenado = convertir_cadena_para_almacenar(iv)

            '''Guardar los datos recuperados/creados anteriormente antes de mandarlos a la base de datos'''
            usuarios = models.Usuarios()
            usuarios.nombre = lista[0]
            usuarios.nick = lista[1]
            usuarios.password = password_hasheado
            usuarios.correo = correo
            usuarios.chatID = chat_id
            usuarios.tokenT = token_telegram
            usuarios.llave_privada = llave_privada
            usuarios.llave_publica = llave_publica
            usuarios.iv = iv_almacenado
            usuarios.salt = salt_almacenado

            '''Manejo de errores y enviar los datos a la base de datos (en caso de que no existan errores)'''
            errores = recolectar_errores_registro(usuarios, password_confirmacion_hasheado, password)
            if not errores:
                usuarios.save()
                logging.info("usuario resgitrado:" + nick)
                return redirect('/formulario_registro')
            else:
                contexto = {'errores': errores, 'usuarios': usuarios}
                return render(request, template, contexto)
        else:
            return HttpResponse('Agotaste tus intentos espera 1 minuto')

@login_requerido2
def logout(request):
    request.session.flush()
    return redirect('/login')

@login_requerido
def logout(request):
    request.session.flush()
    return redirect('/login')
    
@login_requerido2
def pagina(request):
    template = 'inicial.html'
    if request.method == 'GET':
        return render(request, template)
        
def existe_usuario_asociado(usuario):
	 nicks_almacenados = list(models.Usuarios.objects.values_list('nick').distinct())
	 for nick in nicks_almacenados:
	 	nick = ','.join(nick)
	 	if nick == usuario:
	 		return True
	 	else:
	 		return False

def generar_master_password():
	 caracteres = string.ascii_letters + string.digits + string.punctuation
	 dimension = 16
	 return ''.join(random.choice(caracteres) for _ in range(dimension))

''' Crea un iv y una llave aes para cifrar la contraseña proporcionada por el usuario '''
def cifrar_password_credenciales(password):
	 iv = os.urandom(16)
	 master_password = generar_master_password()
	 llave_aes = generar_llave_aes_from_password(master_password)
	 password = password.encode('utf-8')
	 password_cifrado = cifrar(password, llave_aes, iv)
	 password = convertir_cadena_para_almacenar(password_cifrado)
	 iv = convertir_cadena_para_almacenar(iv)
	 return password, iv, master_password

@login_requerido2
def formulario_credenciales(request):
	 nick = request.session.get('usuario', 'anonimo')
	 template = 'credencialesFormulario.html'
	 if request.method == 'GET':
		  return render(request, template)
	 elif request.method == 'POST':
   	  nombreCuenta = request.POST.get('nomSitio', '').strip()
   	  usuario = request.POST.get('usuario', '').strip()
   	  url = request.POST.get('url', '').strip()
   	  detallesExtra = request.POST.get('extra', '').strip()
   	  password = request.POST.get('password', '').strip()
   	  
   	  llave_foranea = models.Usuarios.objects.get(nick=nick)   	  
   	  
   	  password, iv, master_password = cifrar_password_credenciales(password)
   	  
   	  credenciales = models.Credenciales()
   	  credenciales.nombreCuenta = nombreCuenta
   	  credenciales.usuario = usuario
   	  credenciales.iv = iv
   	  credenciales.password = password
   	  credenciales.url = url
   	  credenciales.detallesExtra = detallesExtra
   	  credenciales.id_usuario = llave_foranea
   	  credenciales.master_password = master_password   	  	
   	  credenciales.save()
   	  logging.info("el usuario:" + usuario + "registro las credenciales de la cuenta" + nombreCuenta)
   	  return redirect('/pagina')

'''Función que toma los passwords asociados a las credenciales del usuario para obtenerlos descifrados '''
def descifrar_passwords(datos_almacenados):
	 numero = 0
	 for registro in datos_almacenados:
	 	iv = registro.iv
	 	master_password = registro.master_password
	 	password_almacenado = registro.password
	 	iv = convertir_almacenado_a_original(iv)
	 	password_cifrado = convertir_almacenado_a_original(password_almacenado)
	 	llave_aes = generar_llave_aes_from_password(master_password)
	 	password = descifrar(password_cifrado, llave_aes, iv)
	 	password_original = password.decode('utf-8')
	 	datos_almacenados[numero].password = password_original
	 	numero+=1
	 return datos_almacenados
	 
@login_requerido2  	  	
def ListaAsociados(request):
    template = 'asociadas.html'
    nick = request.session.get('usuario', 'anonimo')
    if request.method == 'GET':
    	datos_almacenados = models.Usuarios.objects.get(nick=nick)
    	Credencial = models.Credenciales.objects.filter(id_usuario=datos_almacenados)
    	Credencial = descifrar_passwords(Credencial)
    	return render(request, template ,{"Credencial": Credencial})
    elif request.method == 'POST':
    	id_cuenta = request.POST.get('idCuenta', '').strip()
    	cuenta = request.POST.get('nombreCuenta', '').strip()
    	usuario = request.POST.get('usuario', '').strip()
    	password = request.POST.get('password', '').strip()
    	url = request.POST.get('url', '').strip()
    	detalles_extra = request.POST.get('extra', '').strip()
    	
    	password, iv, master_password = cifrar_password_credenciales(password)
    	
    	models.Credenciales()
    	models.Credenciales.objects.filter(pk=id_cuenta).update(nombreCuenta=cuenta, usuario=usuario, password=password, iv=iv, master_password=master_password, url=url, detallesExtra=detalles_extra)
    	logging.info("el usuario: " + usuario + "edito una cuenta: " + cuenta)
    	return redirect('/pagina')