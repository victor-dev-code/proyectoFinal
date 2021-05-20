
from django.template import Template, Context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import os, html, re, string, requests, base64, sys, datetime
from pagina1 import models
from .utils import generar_hash, convertir_cadena_para_almacenar, validar_password, convertir_almacenado_a_original, validar_usuario, validar_password_almacenado
from .cifrar_aes import generar_llave_aes_from_password, cifrar, descifrar
from .generarLlaves import generar_llave_privada, generar_llave_publica, convertir_llave_privada_bytes, convertir_llave_publica_bytes, convertir_bytes_llave_privada, convertir_bytes_llave_publica
from GestionClaves.decoradores import login_requerido
from .bot import mandar_mensaje_bot
from datetime import timezone

def ip_cliente(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def intento_ip(ip):
    guardar_registro = models.IntentosIP.objects.filter(llave_primaria=ip)
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

@login_requerido
def token(request):
    template = 'token.html'
    if request.method == 'GET':
        logueado = request.session.get('logueado', False)
        if logueado:
            return redirect('/pagina')
        return render(request, template)

    elif request.method == 'POST':
        token = request.POST.get('token', '').strip()

def login(request):
    template = 'login.html'
    if request.method == 'GET':
        logueado = request.session.get('logueado', False)
        if logueado:
            mensaje = base64.b64encode(os.urandom(5)).decode('utf-8')
            mensaje = mandar_mensaje_bot(mensaje)
            return redirect('/token')
        return render(request, template)
    elif request.method == 'POST':
        nick = request.POST.get('nick', '').strip()
        password = request.POST.get('contraseña', '').strip()
        nick = html.escape(nick)
        password = html.escape(password)
        password = validar_password(password)
        try:
            models.Usuarios.objects.get(nick=nick, password=password)
            request.session['logueado'] = True
            request.session['usuario'] = nick
            return redirect('/token')
        except:
            errores = ['credenciales de usuario o nick incorrectos']
            return render(request, template, {'errores': errores})

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
    if len(password) < 8:
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
    chat_id = models.Usuarios.objects.filter(chat_id=usuarios.chatID)
    if len(chat_id) > 0:
        return True
    return False

def token_repetido(usuarios):
    token = models.Usuarios.objects.filter(token=usuarios.tokenT) 
    if len(token) > 0:
        return True
    return False 

def recolectar_errores_registro(usuarios, confirmacion, password):
    errores = []
    expresion_regular_email = re.compile(r'^[a-zA-Z0-9_\-\.~]{2,}@[a-zA-Z0-9_\-\.~]{2,}\.[a-zA-Z]{2,4}$')
    expresion_regular_token_telegram = re.compile(r'^[0-9]{10}:[a-zA-Z0-9_-]{35}$')
    if usuarios.nombre == '':
        errores.append('El campo nombre completo está vacío')
    if len(usuarios.nombre) < 15:
        errores.append('El campo nombre completo debe contener al menos 20 caracteres')
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


def logout(request):
    request.session.flush()
    return redirect('/login')