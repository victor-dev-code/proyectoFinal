
from django.template import Template, Context
from django.shortcuts import render, redirect
import os, html, re, string, requests, base64, sys
from GestionClaves.decoradores import login_requerido
from .bot import mandar_mensaje_bot
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

def logout(request):
    request.session.flush()
    return redirect('/login')