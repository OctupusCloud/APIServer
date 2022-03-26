from django.contrib import admin
from .models import *

class ViewDevices(admin.ModelAdmin):
    list_display = ("name","memory","vendor","family")
    search_fields = ("name",)

class ViewInterfaces(admin.ModelAdmin):
    list_display = ("device", "type", "slot", "port", "ip4_address", "status")
    search_fields = ("type",)

class ViewUsuarios(admin.ModelAdmin):
    list_display = ("usuario", "password")
    search_fields = ("usuario",)

admin.site.register(Devices, ViewDevices)
admin.site.register(Interfaces, ViewInterfaces)
admin.site.register(Usuarios, ViewUsuarios)