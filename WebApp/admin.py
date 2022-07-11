from django.contrib import admin
from ApiApp.models import *
from WebApp.models import *

class ViewDevices(admin.ModelAdmin):
    list_display = ("name","memory","vendor","family")
    search_fields = ("name",)

class ViewInterfaces(admin.ModelAdmin):
    list_display = ("device", "type", "slot", "port", "ip4_address", "status")
    search_fields = ("type",)

class ViewUsuarios(admin.ModelAdmin):
    list_display = ("usuario", "password")
    search_fields = ("usuario",)

class ViewTokens(admin.ModelAdmin):
    list_display = ("token", "name")
    search_fields = ("name",)

admin.site.register(Devices, ViewDevices)
admin.site.register(Interfaces, ViewInterfaces)
admin.site.register(Usuarios, ViewUsuarios)
admin.site.register(Tokens, ViewTokens)