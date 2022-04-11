from ipaddress import ip_address
from os import name
from django.http import HttpResponse
from django.shortcuts import render
import json
import base64
from WebApp.models import Interfaces, Devices, Usuarios
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
            datos = f"Problemas con la autorización"

        return HttpResponse(datos)
    else:
        msg = f"Método {request.method} no sportado"
        return HttpResponse(msg)

@csrf_exempt
def interfaces(request, _device):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=_device).values())
            datos = json.dumps(registros) 
        else:
            datos = f"Problemas con la autorización"

        return HttpResponse(datos)
    elif request.method == "POST":
        expected_keys = ["device","type","slot","port","ip4_address","status"]
        body = json.loads(request.body.decode('utf-8'))
        keys = list(body.keys())
        if keys == expected_keys:
            if check_values(body):
                device_v = Devices.objects.get(name=body["device"])
                if str(device_v) == str(_device):
                    type_v = body["type"]
                    slot_v = body["slot"]
                    port_v = body["port"]
                    ip_address_v = body["ip4_address"]
                    status_v = body["status"]
                    obj, created = Interfaces.objects.get_or_create(device=device_v,
                                                                    type=type_v,
                                                                    slot=slot_v,
                                                                    port=port_v,
                                                                    ip4_address=ip_address_v,
                                                                    status=status_v)
                    if created:
                        msg = f"Registro creado, id {obj.id}"
                    else:
                        msg = f"Registro existente, id {obj.id}"
                else:
                    msg = f"Parámetro <device> incorrecto en URL, debe ser {device_v}"
            else:
                msg = f"Body incorrecto, bad values {json.dumps(body)}"
        else:
            msg = f"Body incorrecto, bad keys {keys}"

        return HttpResponse(msg) 
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

        else:
            datos = f"Problemas con la autorización"

        return HttpResponse(datos)
    else:
        msg = f"Método {request.method} no sportado"
        return HttpResponse(msg)

def check_values(_body):
    if isinstance(_body['device'], str) and isinstance(_body['device'], str) and isinstance(_body['ip4_address'], str) and isinstance(_body['status'], str):
        if isinstance(_body['slot'], int) and isinstance(_body['slot'], int):
            return True
        else:
            return False
    else:
        return False
