from django.shortcuts import render, redirect

def login_requerido(vista):
	def interna(request, *args, **kwargs):
		logueado = request.session.get('logueado', False)
		if not logueado:
			return redirect('/login')
		return vista(request, *args, **kwargs)
	return interna


def login_requerido2(vista):
	def interna(request, *args, **kwargs):
		logueado2 = request.session.get('logueado2', False)
		if not logueado2:
			return redirect('/pagina')
		return vista(request, *args, **kwargs)
	return interna