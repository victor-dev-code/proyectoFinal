from django.shortcuts import render, redirect

def login_requerido(vista):
	def interna(request, *args, **kwargs):
		logueado = request.session.get('logueado', False)
		if not logueado:
			return redirect('/login')
		return vista(request, *args, **kwargs)
	return interna
