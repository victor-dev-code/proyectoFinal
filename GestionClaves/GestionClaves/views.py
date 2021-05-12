
from django.template import Template, Context
from django.shortcuts import render, redirect
import os, html, re, string, base64

def login(request):
    template = 'login.html'
    if request.method == 'GET':
        logueado = request.session.get('logueado', False)
        if logueado:
            return redirect('/pagina')
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
            return redirect('/pagina')
        except:
            errores = ['credenciales de usuario o nick incorrectos']
            return render(request, template, {'errores': errores})

def logout(request):
    request.session.flush()
    return redirect('/login')