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
    if auth_decoded[0] == "oction" and auth_decoded[1] == "Scrimaglia":
        return True
    else:
        return False


def devices(request):
    auth = basic_authorization(request)
    if auth:
        datos = {
            "device": "Catalyst2900",
            "datos": {
                "family": "Low End Switch",
                "interfaces": ["Giga0", "Giga1", "Giga2"]
            }
        }
        return HttpResponse(json.dumps(datos))
    else:
        msg = f"Problemas con la autorización"
        return HttpResponse(msg)

def interfaces(request, device):
    msg = f"metodo {request.method}, device {device}"   
    return HttpResponse(msg)
