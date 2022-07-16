# ApiServer project
# By Ed Scrimaglia
# WebApp

from pickle import FALSE
from turtle import up
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from py import code
from ApiApp.models import Interfaces, Devices, Tokens, Usuarios

# Create your views here.

def home(request):
    return render(request,"main.html")

def about(request):
    return render(request,"about.html")

def apidevices(request):
    return render(request,"apidevices.html")

def process_sub_pag(request):
    if request.method == 'GET':
        if 'device' in str(request.get_full_path()):
            registros = Devices.objects.all().order_by('name').values()
            if len(registros) >= 1:
                devices_v = {
                    'data': registros,
                    'cant_rec': len(registros)
                }
            else:
                devices_v = {
                    'result': f"No hay Devices registrados",
                    'cant_rec': 0
                }
        
            return render(request,"devices.html",devices_v)
        elif 'interfaces' in str(request.get_full_path()):
            registros = Interfaces.objects.all().order_by('device_id', 'type', 'slot', 'port').values()
            if len(registros) >= 1:
                devices_v = {
                    'data': registros,
                    'cant_rec': len(registros)
                }
            else:
                devices_v = {
                    'result': f"No hay Interfaces registradas",
                    'cant_rec': 0
                }
        
            return render(request,"interfaces.html",devices_v)
        elif 'usuarios' in str(request.get_full_path()):
            registros = Usuarios.objects.all().order_by('usuario').values()
            if len(registros) >= 1:
                devices_v = {
                    'data': registros,
                    'cant_rec': len(registros)
                }
            else:
                devices_v = {
                    'result': f"No hay Usuarios registrados",
                    'cant_rec': 0
                }
        
            return render(request,"usuarios.html",devices_v)
        elif 'token' in str(request.get_full_path()):
            registros = Tokens.objects.all().order_by('name').values()
            if len(registros) >= 1:
                devices_v = {
                    'data': registros,
                    'cant_rec': len(registros)
                }
            else:
                devices_v = {
                    'result': f"No hay Tokens registrados",
                    'cant_rec': 0
                }
        
            return render(request,"tokens.html",devices_v)
        else:
            return HttpResponse("Bad URL, check process_sub_pag method in views")
    else:
        return HttpResponse("Must be a GET request")

def copy_text_python(request,texto):
    texto = {
            "to_clipboard": {
                [
                    "import requests",
                    "import json",
                    "url = 'http://apiserver.octupus.com/api/v1/devices'",
                    "headers = {",
                    "'Authorization': 'Token c26b519346e0755bf9b864c0db8d3d36d854ab23'",
                    "'Content-Type': 'application/json'",
                    "}",
                    "response = requests.request('GET', url, headers=headers, data=payload)",
                    "}"
                ]
            },
    }

    return JsonResponse(texto, safe=False)