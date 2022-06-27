# ApiServer project
# By Ed Scrimaglia

from asyncore import write
from codecs import encode
#from encodings import utf_8
#import imp
from ipaddress import ip_address
#from json import encoder
from os import name
from pickle import FALSE
from turtle import up
#from queue import Empty
#import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64
from py import code
from pymysql import NULL, IntegrityError
from tomlkit import item
#from requests import Response
#from yaml import safe_dump, serialize
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
    auth = basic_authorization(request)
    msg = ''
    if auth:
        if request.method == "GET":
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).values())
            if len(registros) >= 1:
                output_dict = create_output(registros)
                return JsonResponse(output_dict, safe=False)
            else:
                msg = {"result": f"no hay registros. Check URL device '{_device}'"}

            return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))
        elif request.method == "POST":
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
                            obj, created = Interfaces.objects.get_or_create(
                                device=device_v,
                                type=type_v,
                                slot=slot_v,
                                port=port_v,
                                ip4_address=ip_address_v,
                                status=status_v)
                            if created:
                                msg = {"result": f"Interfaz tipo: {type_v}, slot: {slot_v}, port: {port_v}, en device {device_v}, created"}
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
        elif request.method == "PATCH":
            expected_keys = ["type","slot","port","ip4_address","status"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if all(item in expected_keys for item in keys):
                if check_values(body):
                    try:
                        device_v = Devices.objects.get(name=(str(_device).strip()))
                        type_v = body["type"]
                        slot_v = body["slot"]
                        port_v = body["port"]
                        ip_address_v = body["ip4_address"] if "ip4_address" in body else False
                        status_v = body["status"] if "status" in body else False
                        try:
                            obj = Interfaces.objects.get(device=device_v,slot=slot_v,port=port_v)
                            obj.ip4_address = ip_address_v if ip_address_v else obj.ip4_address
                            obj.status = status_v if status_v else obj.status
                            obj.save()
                            msg = {"result": f"Interfaz tipo: {type_v}, slot: {slot_v}, port: {port_v}, en device {device_v}, updated"}
                        except Interfaces.DoesNotExist as error:
                            msg = {"result": f"Interfaz no existe"}
                    except Devices.DoesNotExist as error:
                        msg = {"result": f"No existe device '{_device}'. Check URL"}
            else:
                msg = {"result": f"Body incorrecto, bad keys {keys}"}
        elif request.method == "DELETE":
            expected_keys = ["type","slot","port"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if keys == expected_keys:
                device_v = Devices.objects.get(name=(str(_device).strip()))
                type_v = body["type"]
                slot_v = body["slot"]
                port_v = body["port"]
                try:
                    obj = Interfaces.objects.filter(device=device_v,type=type_v,slot=slot_v,port=port_v).delete()
                    msg = {"result": f"Interfaz tipo: {type_v}, slot: {slot_v}, port: {port_v}, en device {device_v}, deleted"}
                except Interfaces.DoesNotExist as error:
                    msg = {"result": f"Interfaz no existe"}
            else:
                msg = {"result": f"Body incorrecto, bad keys {keys}"}
        else:
            msg = {"result": f"Método {request.method} no permitido"}
    else:
        msg = {"result": f"Problemas con la autorización"}

    return JsonResponse(msg, safe=False)

@csrf_exempt
def interfaces_status(request, _device, _status):
    if request.method == "GET":
        auth = basic_authorization(request)
        if _status.lower() == "up":
            status_v = "u"
        elif _status.lower() == "down":
            status_v = "d"
        if auth:
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).values() & Interfaces.objects.filter(status=status_v).values())
            if len(registros) >= 1:
                ouput_dict = create_output(registros)
                return JsonResponse(ouput_dict, safe=False)
            else:
                msg = {"result": f"no hay registros. Check URL device '{_device}' o status '{_status}'"}
        else:
            msg = {"result": f"Problemas con la autorización"}
    else:
        msg = {"result": f"Método {request.method} no sportado"}

    return JsonResponse(msg, safe=False)

def check_values(_body):
    if  'type' in _body:
        if  isinstance(_body['type'], str):
            result = True
        else:
            result = False
    if 'ip4_address' in _body:
        if isinstance(_body['ip4_address'], str):
            result = True
        else:
            result = False
    if 'status' in _body:
        if isinstance(_body['status'], str):
            result = True
        else:
            result = False
    if 'slot' in _body:
        if isinstance(_body['slot'], int):
            result = True
        else:
            result = False
    if 'port' in _body:
        if isinstance(_body['port'], int):
            result = True
        else:
            result = False
    if result:
        return True
    else:
        return False

@csrf_exempt
def api_test(request):
    headers_o = dict(request.headers)
    api_test = dict()
    headers_auth = dict()

    for key,value in headers_o.items():
        if key == "Authorization":
            tipo_auth = request.headers['Authorization'].split()[0]
            credentials = get_credentials(request,tipo_auth)
            auth_v = dict()
            if "Basic" in tipo_auth:
                auth_v['Tipo'] = credentials[0]
                auth_v['Encoded'] = value
                auth_v['User'] = credentials[1]
                auth_v['Password'] = credentials[2]
            else:
                auth_v['Tipo'] = credentials[0]
                auth_v['Encoded'] = credentials[1]
            headers_auth[key] = auth_v
        else:    
            headers_auth[key] = value

    api_test['Headers'] = headers_auth
    api_test['Method'] = request.method
    api_test['Msg'] = f"Welcome to ApiServer by OctUPus - Ed Scrimaglia, Año 2022"
    
    api_test_result = dict()
    api_test_result['test_result'] = api_test

    return JsonResponse(api_test_result, safe=False)

def get_credentials(request, tipo):
    auth = request.headers['Authorization'].split()[1]
    cred_l = list()
    if "Basic" in tipo:
        auth_decoded = base64.b64decode(auth).decode('utf-8').split(":")
        usuario_h = auth_decoded[0]
        password_h = auth_decoded[1]
        cred_l.append(tipo)
        cred_l.append(usuario_h)
        cred_l.append(password_h)
    elif "Bearer" in tipo:
        cred_l.append("Token")
        cred_l.append(auth)
    else:
        cred_l.append(tipo)
        cred_l.append(auth)
    
    return cred_l

def create_output(registros):
    output_dict = list(dict())
    try:
        for object in registros:
            object.pop("id", None)
            output_dict.append({
                "type": "FastEthernet" if object["type"] == "Fast" else "GigabitEhernet",
                "slot": object["slot"],
                "port": object["port"],
                "ipv4_address": object["ip4_address"],
                "status": "Up" if object["status"] == "u" else "Down"
            })
    except Exception as error:
        return {"resutl": str(error)}
        
    return output_dict
