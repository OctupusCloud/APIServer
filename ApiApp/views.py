# ApiServer project
# By Ed Scrimaglia
# ApiApp

from asyncore import write
from codecs import encode
from ipaddress import ip_address
#from operator import itemgetter
from pickle import FALSE
from turtle import up
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64
from jmespath import search
from py import code
from pymysql import NULL, IntegrityError
from tomlkit import item
from ApiApp.models import Interfaces, Devices, Tokens, Usuarios
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from urllib.parse import unquote
import ipaddress 

# The Views and the Logic

def get_authorization(request):
    auth_method = request.headers['Authorization'].split()[0]
    if 'basic' in auth_method.lower():
        auth = request.headers['Authorization'].split()[1]
        auth_decoded = base64.b64decode(auth).decode('utf-8').split(":")
        usuario_h = str(auth_decoded[0]).strip()
        password_h = str(auth_decoded[1]).strip()
        registro = list(Usuarios.objects.filter(usuario=usuario_h).values())
        if len(registro) == 1:
            password_db = str(registro[0]['password']).strip()
            if password_h == password_db:
                return True
            else:
                return False
        else:
            return False
    elif auth_method.lower() in ['bearer','token']:
        token_v = str(request.headers['Authorization'].split()[1]).strip()
        registro = list(Tokens.objects.filter(token=token_v).values())
        if len(registro) == 1:
            if token_v == str(registro[0]['token']).strip():
                return True
            else:
                return False
        else:
            return False
    else:
        return False


@csrf_exempt
def devices(request):
    auth = get_authorization(request)
    if auth:
        if request.method == "GET":
            registros = list(Devices.objects.all().order_by('name').values())
            if len(registros) >= 1:
                output_dict = create_output(registros,Devices) 
                return JsonResponse(output_dict, safe=False)
            else:
                msg = {"result": f"No hay Devices registrados"}
        else:
            msg = {"result": f"Método {request.method} no permitido, endpoint {unquote(request.get_full_path())}"}
    else:
        msg = {"result": f"Problemas con la autorización"}
    
    return JsonResponse(msg, safe=False)


@csrf_exempt
def interfaces(request, _device):
    auth = get_authorization(request)
    msg = '' 
    reason = ''
    if auth:
        if request.method == "GET":
            registros = list(Interfaces.objects.filter(device=str(_device).strip()).order_by('device_id', 'type', 'slot', 'port').values())
            if len(registros) >= 1:
                output_dict = create_output(registros,Interfaces)
                return JsonResponse(output_dict, safe=False)
            else:
                msg = {"result": f"no hay registros. Check URL: device '{_device}'"}

            return HttpResponse(json.dumps(msg, ensure_ascii=False).encode("utf-8"))
        elif request.method == "POST":
            expected_keys = ["type","slot","port","ip4_address","status"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if keys == expected_keys:
                correct_body, reason = check_values(body,request.method)
                if correct_body:
                    try:
                        device_v = Devices.objects.get(name=(str(_device).strip()))
                        type_v = cast_inter_type_input(body["type"],device_v)
                        slot_v = body["slot"]
                        port_v = body["port"]
                        ip_address_v = body["ip4_address"]
                        status_v = cast_inter_status_input(body["status"])
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
                                msg = {"result": f"Interfaz existente"}
                        except IntegrityError as error:
                            msg = {"result": f"IP Address duplicada"}
                    except ObjectDoesNotExist as error:
                        msg = {"result": f"No existe device '{_device}'. Check URL"}
                else:
                    msg = {"result": f"Body incorrecto, {reason}"}
            else:
                msg = {"result": f"Body incorrecto, must be {expected_keys}"}
        elif request.method == "PATCH":
            expected_keys = ["type","slot","port","ip4_address","status"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if all(item in expected_keys for item in keys):
                correct_body, reason = check_values(body,request.method)
                if correct_body:
                    try:
                        device_v = Devices.objects.get(name=(str(_device).strip()))
                        type_v = cast_inter_type_input(body["type"],device_v)
                        slot_v = body["slot"]
                        port_v = body["port"]
                        ip_address_v = body["ip4_address"] if "ip4_address" in body else False
                        status_v = cast_inter_status_input(body["status"]) if "status" in body else False
                        try:
                            obj = Interfaces.objects.get(device=device_v,type=type_v,slot=slot_v,port=port_v)
                            obj.ip4_address = ip_address_v if ip_address_v else obj.ip4_address
                            obj.status = status_v if status_v else obj.status
                            obj.save()
                            msg = {"result": f"Interfaz tipo: {type_v}, slot: {slot_v}, port: {port_v}, en device {device_v}, modified"}
                        except Interfaces.DoesNotExist as error:
                            msg = {"result": f"Interfaz no existe"}
                    except Devices.DoesNotExist as error:
                        msg = {"result": f"No existe device '{_device}'. Check URL"}
                else:
                    msg = {"result": f"Body incorrecto, {reason}"}
            else:
                msg = {"result": f"Body incorrecto, must be ['type','slot','port' and 'ip4_address' or 'status']"}
        elif request.method == "DELETE":
            expected_keys = ["type","slot","port"]
            body = json.loads(request.body.decode('utf-8'))
            keys = list(body.keys())
            if keys == expected_keys:
                device_v = Devices.objects.get(name=(str(_device).strip()))
                type_v = cast_inter_type_input(body["type"],device_v)
                slot_v = body["slot"]
                port_v = body["port"]
                try:
                    Interfaces.objects.get(device=device_v,type=type_v,slot=slot_v,port=port_v).delete()
                    msg = {"result": f"Interfaz tipo: {type_v}, slot: {slot_v}, port: {port_v}, en device {device_v}, deleted"}
                except Interfaces.DoesNotExist as error:
                    msg = {"result": f"Interfaz no existe"}
            else:
                msg = {"result": f"Body incorrecto, bad keys {keys}. Must be ['type','slot',''port]"}
        else:
            msg = {"result": f"Método {request.method} no permitido, endpoint {unquote(request.get_full_path())}"}
    else:
        msg = {"result": f"Problemas con la autorización"}

    return JsonResponse(msg, safe=False)


@csrf_exempt
def interfaces_status(request, _device, _status):
    auth = get_authorization(request)
    if auth:
        try:
            if request.method == "GET":
                status_v = cast_inter_status_input(_status)
                registros = list(Interfaces.objects.filter(device=str(_device).strip()).order_by('device_id', 'type', 'slot', 'port').values() 
                    & Interfaces.objects.filter(status=status_v).order_by('device_id', 'type', 'slot', 'port').values())
                if len(registros) >= 1:
                    ouput_dict = create_output(registros,Interfaces)
                    return JsonResponse(ouput_dict, safe=False)
                else:
                    msg = {"result": f"no hay registros. Check URL: device '{_device}' o status '{_status}'"}
            else:
                msg = {"result": f"Método {request.method} no permitido, endpoint {unquote(request.get_full_path())}"}
        except Exception as error:
            msg = {"result": f"error"}
    else:
         msg = {"result": f"Problemas con la autorización"}

    return JsonResponse(msg, safe=False)


def check_values(_body,_method):
    if  'type' in _body:
        if  isinstance(_body['type'], str):
            if 'slot' in _body:
                if isinstance(_body['slot'], int) and _body['slot'] in range(0,10):
                    if 'port' in _body:
                        if isinstance(_body['port'], int) and _body['port'] in range(0,2):
                            msg = f"Body correcto"
                        else:
                            msg = f"key 'port' no es tipo integer o esta fuera de rango (0,9)"
                            return False, msg
                    else:
                        msg = f"Body no contiene key 'port'"
                        return False, msg
                else:
                    msg = f"key 'slot' no es tipo integer o esta fuera de rango (0,9)"
                    return False, msg
            else:
                msg = f"Body no contiene key 'slot'"
                return False, msg
        else:
            msg = f"key 'type' no es tipo string"
            return False, msg
    else:
        msg = f"Body no contiene key 'type'"
        return False, msg

    if _method == 'POST':
        if 'ip4_address' in _body:
            if isinstance(_body['ip4_address'], str):
                correct_address, msg = validate_ip_address(_body['ip4_address'])
                if correct_address:
                    if 'status' in _body:
                        if isinstance(_body['status'], str):
                            msg = f"Body correcto"
                            return True, msg
                        else:
                            msg = f"key 'status' no es tipo string"
                            return False, msg
                    else:
                        msg = f"Body no contiene key 'status'"
                else:
                    return False, msg
            else:
                msg = f"key 'ip4_address' no es tipo string"
                return False, msg
        else:
            msg = f"Body no contiene key 'ip4_address'"
            return False, msg
    elif _method == 'PATCH':
        isPatchCorrect = False
        if 'ip4_address' in _body:
            if isinstance(_body['ip4_address'], str):
                correct_address, msg = validate_ip_address(_body['ip4_address'])
                if correct_address:
                    msg = f"Body correcto"
                    isPatchCorrect = True
                else:
                    return False, msg 
            else:
                msg = f"key 'ip4_address' no es tipo string"
                return False, msg
        if 'status' in _body:
            if isinstance(_body['status'], str):
                msg = f"Body correcto"
                isPatchCorrect = True
            else:
                msg = f"key 'status' no es tipo string"
                return False, msg
        
        if isPatchCorrect:
            msg = "what"
            return True, msg
        else:
            msg = f"Body no contiene los keys 'ip4_addres' ni 'status'"
            return False, msg
    else:
        msg = f"Body checking for Método incorrecto {_method}"
        return False, msg

   
def validate_ip_address(address):
    try:
        ip = ipaddress.ip_address(address)
        msg = f"IP address {address} is valid."
        status = True
    except ValueError:
        msg = f"IP address {address} is not valid"
        status = False
    return  status, msg


@csrf_exempt
def apitest(request):
    api_test_result = dict()
    api_test_result['method'] = request.method
    api_test_result['result'] = "API Test Up and running"

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


def create_output(_registros, _model):
    output_dict = list()
    try:
        for object in _registros:
            if _model == Interfaces:
                output_dict.append({
                    "type": "FastEthernet" if object["type"] == "Fast" else "GigabitEhernet",
                    "slot": object["slot"],
                    "port": object["port"],
                    "ip4_address": object["ip4_address"],
                    "status": "Up" if object["status"] == "u" else "Down"
                })
            elif _model == Devices:
                output_dict.append({
                    "name": object["name"],
                    "memory":  object["memory"],
                    "vendor": object["vendor"],
                    "family": object["family"],
                })
    except Exception as error:
        return {"resutl": str(error)}
        
    return output_dict


def cast_inter_type_input(_type,_device):
    if 'fastethernet'.find(_type.lower()) != -1:
        return "Fast"
    elif 'gigabitethernet'.find(_type.lower()) != -1:
        return "Giga"
    else:
        if str(_device).strip() == 'Catalyst 2900':
            return "Fast"
        else:
            return "Giga"


def cast_inter_status_input(_status):
    if 'up'.find(_status.lower()) != -1:
        return "u"
    else:
        return "d"
