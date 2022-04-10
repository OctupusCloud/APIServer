# Projecto API Server

## Objetivo: programar un API Server utilizando Django. Django es un framework escrito en Python para desarrollar aplicaciones web

## API endpoints

### api/v1/devices

Descripción: retorna los dispositvos almacenados en la DB  
Métodos:
GET  

### api/v1/{device}/interfaces

Descripción: agrega, elimina, modifica y retorna las interfaces de un {dispositivo} almacenaodo en la DB  

Métodos:  
GET  
POST  
  Body:  
  {  
    "device": "device name",  
    "type": "Giga" o "Fast", 
    "slot": 0 o 1,  
    "port": 0 o 1,  
    "ip_address": "X.X.X.X" o "none",  
    "status": "Up" o "Down"  
  }  
PATCH  
 Body:  
  {  
    "id": id, (registro a modificar)  
    atributo a cambiar en formato Key/Value  
  }  
DELETE  
 {  
    "id": id, (registro a eliminar)  
  }  

### api/v1/{device}/interfaces/{status}

Descripción: retorna las interfaces de un {dispositivo} almecenado en la DB según su estado {Up o Down}  

Métodos:  
GET  

## Base de datos

SQLite  

## Tablas DB

Devices  
Interfaces  
Usuarios  

### Ed Scrimaglia, Año 2022
