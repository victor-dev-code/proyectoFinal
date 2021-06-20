
from django.template import Template, Context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import os, html, re, string, requests, base64, sys, datetime
from pagina1 import models
from .utils import generar_hash, convertir_cadena_para_almacenar, validar_password, convertir_almacenado_a_original, validar_usuario, validar_password_almacenado
from .cifrar_aes import generar_llave_aes_from_password, cifrar, descifrar
from .generarLlaves import generar_llave_privada, generar_llave_publica, convertir_llave_privada_bytes, convertir_llave_publica_bytes, convertir_bytes_llave_privada, convertir_bytes_llave_publica
from GestionClaves.decoradores import login_requerido, login_requerido2
from datetime import timezone

'''mandar mensaje bot telegram'''
def mandar_mensajeBot(request):
    nick = request.session.get('usuario', 'anonimo')
    datos_usuarios = models.Usuarios.objects.get(nick=nick)
    chat_id = datos_usuarios.chatID
    token = datos_usuarios.tokenT
    mensaje = base64.b64encode(os.urandom(5)).decode('utf-8')
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + mensaje
    requests.get(send_text)
    ''' guaradar token enviado a telegram en la base de datos '''
    models.Usuarios()
    models.Usuarios.objects.filter(nick=nick).update(tokenEnviado=mensaje)
    


''' ibtener ip del cliente '''
def ip_cliente(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
''' intento de las ip del cliente '''
def intento_ip(ip):
    guardar_registro = models.IntentosIP.objects.filter(pk=ip)
    if not guardar_registro:
        registro = models.IntentosIP(ip=ip, cont=1, last_Peticion=datetime.datetime.now())
        registro.save()
        return True
    guardar_registro = guardar_registro[0]
    diferencia_tiempo = tiempo_ahora(guardar_registro.last_Peticion)
    if diferencia_tiempo > 60:
        guardar_registro.last_Peticion = datetime.datetime.now()
        guardar_registro.cont = 1
        guardar_registro.save()
        return True
    else:
        if guardar_registro.cont < 3:
             guardar_registro.last_Peticion = datetime.datetime.now()
             guardar_registro.cont += 1
             guardar_registro.save()
             return True
        else:
            guardar_registro.last_Peticion = datetime.datetime.now()
            return False

def tiempo_ahora(tiempo):
    ahora =  datetime.datetime.now(timezone.utc)
    diferencia = ahora - tiempo
    return diferencia.seconds

''' pagina de token'''
@login_requerido
def token(request):
    template = 'token.html'
    if request.method == 'GET':
        return render(request, template)
    elif request.method == 'POST':
        ip = ip_cliente(request)
        if intento_ip(ip):
            token = request.POST.get('token', '').strip()
            try:
                models.Usuarios.objects.get(tokenEnviado=token)
                request.session['logueado2'] = True
                request.session['usuario'] = token
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
        ip = ip_cliente(request)
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
                mandar_mensajeBot(request)
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
        ip = ip_cliente(request)
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

@login_requerido2
def formulario_credenciales(request):
    template = 'credencialesFormulario.html'
    if request.method == 'GET':
        return render(request, template)