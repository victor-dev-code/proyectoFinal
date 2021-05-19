
from django.template import Template, Context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import os, html, re, string, requests, base64, sys, datetime
from pagina1 import models
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
 #       password = validar_password(password)
        try:
            models.Usuarios.objects.get(nick=nick, password=password)
            request.session['logueado'] = True
            request.session['usuario'] = nick
            return redirect('/token')
        except:
            errores = ['credenciales de usuario o nick incorrectos']
            return render(request, template, {'errores': errores})

def logout(request):
    request.session.flush()
    return redirect('/login')