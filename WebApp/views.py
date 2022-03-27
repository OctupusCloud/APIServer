from optparse import Values
from os import name
from django.http import HttpResponse
from django.shortcuts import render
import json
import base64
from WebApp.models import *
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def basic_authorization(request):
    auth = request.headers['Authorization'].split()[1]
    auth_decoded = base64.b64decode(auth).decode('utf-8').split(":")
    usuario_h = auth_decoded[0]
    password_h = auth_decoded[1]
    registro = list(Usuarios.objects.filter(usuario=usuario_h).values())
    if len(registro) == 1:
        password_db = registro[0]['password']
        if password_h == password_db:
            return True
        else:
            return False
    else:
        return False

@csrf_exempt
def devices(request):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Devices.objects.all().values())
            datos = json.dumps(registros)

            return HttpResponse(datos)
        else:
            msg = f"Problemas con la autorización"

            return HttpResponse(msg)
    else:
        msg = f"Método {request.method} no sportado"
        return HttpResponse(msg)

@csrf_exempt
def interfaces(request, _device):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            auth = basic_authorization(request)
            registros = list(Interfaces.objects.filter(device=_device).values())
            salida = json.dumps(registros) 
        else:
            salida = f"Problemas con la autorización"

        return HttpResponse(salida)
    else:
        msg = f"Método {request.method} no permitido"
        return HttpResponse(msg)

@csrf_exempt
def interfaces_status(request, _device, _status):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=_device).values() & Interfaces.objects.filter(status=_status).values())
            datos = json.dumps(registros)

            return HttpResponse(datos)
        else:
            msg = f"Problemas con la autorización"

        return HttpResponse(msg)
    else:
        msg = f"Método {request.method} no sportado"
        return HttpResponse(msg)