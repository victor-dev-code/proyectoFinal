from django.db import models

class Usuarios(models.Model):
    nombre = models.CharField(max_length=50)
    nick = models.CharField(max_length=30)
    password = models.TextField(max_length=1000)
    correo = models.CharField(max_length=70)
    chatID = models.CharField(max_length=9)
    tokenT = models.CharField(max_length=46)
    llave_privada = models.TextField(max_length=400)
    llave_publica = models.TextField(max_length=300)
    iv = models.CharField(max_length=24)
    salt = models.CharField(max_length=100)
    tokenEnviado = models.CharField(max_length=8)

class IntentosIP(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    cont = models.IntegerField(default=0)
    last_Peticion =  models.DateTimeField()


class Credenciales(models.Model):
    nombreCuenta = models.CharField(max_length=20)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    iv = models.CharField(max_length=24)
    password = models.TextField(max_length=1000)
    url = models.CharField(max_length=120)
    detallesExtra = models.CharField(max_length=30)
    