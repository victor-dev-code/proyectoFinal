import base64, hashlib
from pagina1 import models

def convertir_cadena_para_almacenar(dato):
    almacenado = base64.b64encode(dato)
    almacenado = almacenado.decode('utf-8')
    return almacenado

def generar_hash(password, salt):
    hasher = hashlib.sha512()
    password_original = password.encode('utf-8')
    hasher.update(password_original + salt)
    contenido = hasher.hexdigest()
    return contenido

def convertir_almacenado_a_original(dato):
    original = dato.encode('utf-8')
    original = base64.b64decode(original)
    return original



def validar_password(password):
    password_binario = password.encode('utf-8')
    salts_almacenados = list(models.Usuarios.objects.values_list('salt').distinct())
    passwords = list(models.Usuarios.objects.values_list('password').distinct())
    for salt in salts_almacenados:
    	hasher = hashlib.sha512()
    	salt = ','.join(salt) 
    	salt = convertir_almacenado_a_original(salt)
    	hasher.update(password_binario + salt)
    	nuevo_hash = hasher.hexdigest()
    	for elemento in passwords:
    	    elemento = ','.join(elemento)
    	    if elemento == nuevo_hash:
    	        return nuevo_hash

def validar_password_almacenado(password_almacenado, salt_almacenado, password):
    password_binario = password.encode('utf-8')
    hasher = hashlib.sha512()
    hasher.update(password_binario + salt_almacenado)
    nuevo_hash = hasher.hexdigest()
    return nuevo_hash == password_almacenado

def validar_usuario(nombre):
    lista_usuarios = list(models.Usuarios.objects.values_list('nick').distinct())
    for usuario in lista_usuarios:
        usuario = ','.join(usuario)
        if nombre == usuario:
            return True