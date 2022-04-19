# ApiServer project
# By Ed Scrimaglia

from asyncore import write
from codecs import encode
from encodings import utf_8
import imp
from ipaddress import ip_address
from json import encoder
from os import name
from pickle import FALSE
from queue import Empty
import re
from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64
from py import code
from pymysql import NULL, IntegrityError
from requests import Response
from yaml import safe_dump, serialize
from WebApp.models import Interfaces, Devices, Usuarios
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.core import serializers


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
            if len(registros) >= 1:
                for object in registros:
                    object.pop("id", None)
                return JsonResponse(registros, safe=False)
            else:
                msg = {"result": f"no hay registros."}
        else:
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no sportado"}
    
    return JsonResponse(msg, safe=False)


@csrf_exempt
def interfaces(request, _device):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).values())
            if len(registros) >= 1:
                for object in registros:
                    object.pop("id", None)
                return JsonResponse(registros, safe=False)
            else:
                msg = {"result": f"no hay registros. Check URL device '{_device}'"}
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

    return JsonResponse(msg, safe=False)


@csrf_exempt
def interfaces_status(request, _device, _status):
    if request.method == "GET":
        auth = basic_authorization(request)
        if auth:
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).values() & Interfaces.objects.filter(status=_status).values())
            if len(registros) >= 1:
                for object in registros:
                    object.pop("id", None)
                return JsonResponse(registros, safe=False)
            else:
                msg = {"result": f"no hay registros. Check URL device '{_device}' o status '{_status}'"}
        else:
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no sportado"}

    return JsonResponse(msg, safe=False)

def check_values(_body):
    if isinstance(_body['type'], str) and isinstance(_body['ip4_address'], str) and isinstance(_body['status'], str):
        if isinstance(_body['slot'], int) and isinstance(_body['port'], int):
            return True
        else:
            return False
    else:
        return False

@csrf_exempt
def api_test(request):
    headers_o = dict(request.headers)
    headers_r = dict()

    for key,value in headers_o.items():
        if key == "Authorization":
            auth = request.headers['Authorization'].split()[1]
            auth_decoded = base64.b64decode(auth).decode('utf-8').split(":")
            usuario_h = auth_decoded[0]
            password_h = auth_decoded[1]
            auth_v = dict()
            auth_v['Encoded'] = value
            auth_v['User'] = usuario_h
            auth_v['Password'] = password_h
            headers_r[key] = auth_v
        else:    
            headers_r[key] = value

    headers_r['Method'] = request.method
    if bool(request.encoding): 
        headers_r['Encoding'] = request.encoding
    if bool(request.content_params):
        headers_r['Params'] = request.content_params
    if bool(request.COOKIES):
        headers_r['Cookies'] = request.COOKIES
    headers_r['Scheme'] = request.scheme
    if bool(request.GET):
        headers_r['GET'] = request.GET
    if bool(request.POST):
        headers_r['POST'] = request.POST
    headers_r['Status_Code'] = HttpResponse.status_code
    if bool(request.body):
        headers_r['Body'] = json.loads(request.body)

    return JsonResponse(headers_r, safe=False)
