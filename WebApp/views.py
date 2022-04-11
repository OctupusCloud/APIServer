# ApiServer proyect
# By Ed Scrimaglia

from codecs import encode
from encodings import utf_8
from ipaddress import ip_address
from json import encoder
from os import name
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64
from py import code

from pymysql import IntegrityError
from WebApp.models import Interfaces, Devices, Usuarios
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


# The Views and the Logic

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
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no sportado"}
    
    return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))


@csrf_exempt
def interfaces(request, _device):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=_device).values())
            datos = json.dumps(registros) 

            return HttpResponse(datos)
        else:
            msg = {"result": f"Problemas con la autorización"}

        return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))
    elif request.method == "POST":
        auth = basic_authorization(request)
        if auth:
            expected_keys = ["type","slot","port","ip4_address","status"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if keys == expected_keys:
                if check_values(body):
                    try:
                        device_v = Devices.objects.get(name=(str(_device).strip()))
                        type_v = body["type"]
                        slot_v = body["slot"]
                        port_v = body["port"]
                        ip_address_v = body["ip4_address"]
                        status_v = body["status"]
                        try:
                            obj, created = Interfaces.objects.get_or_create(device=device_v,
                                                                            type=type_v,
                                                                            slot=slot_v,
                                                                            port=port_v,
                                                                            ip4_address=ip_address_v,
                                                                            status=status_v)
                            if created:
                                msg = {"result": f"Registro creado, id {obj.id}"}
                            else:
                                msg = {"result": f"Registro existente"}
                        except IntegrityError as error:
                            msg = {"result": f"Registro existente"}
                    except ObjectDoesNotExist as error:
                        msg = {"result": f"No existe device '{_device}'. Check URL"}
                else:
                    msg = {"result": f"Body incorrecto, bad values {body}"}
            else:
                msg = {"result": f"Body incorrecto, bad keys {keys}"}
        else:
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no permitido"}

    return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))


@csrf_exempt
def interfaces_status(request, _device, _status):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).values() & Interfaces.objects.filter(status=_status).values())
            if len(registros) >= 1:
                datos = json.dumps(registros)
                return HttpResponse(datos)
            else:
                msg = {"result": f"no hay registros. Check URL device '{_device}' o status '{_status}'"}
        else:
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no sportado"}

    return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))

def check_values(_body):
    if isinstance(_body['type'], str) and isinstance(_body['ip4_address'], str) and isinstance(_body['status'], str):
        if isinstance(_body['slot'], int) and isinstance(_body['port'], int):
            return True
        else:
            return False
    else:
        return False
