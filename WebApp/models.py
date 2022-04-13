# ApiServer project
# By Ed Scrimaglia

from operator import contains
from tkinter import CASCADE, Widget
from django import forms
from django.db import models
from psutil import users

# Classes & tables.

class Devices(models.Model):
    name = models.CharField(max_length=15, primary_key=True,unique=True)
    memory = models.IntegerField()
    vendor = models.CharField(max_length=50)
    family = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"

status_options = [("u","Up"),("d","Down")]
interface_options = [("Fast","FastEthernet"),("Giga","GigabitEthernet")]
slot_options = [(0,"Slot 0"),(1,"Slot 1")]
port_options = [(0,"Port 0"),(1,"Port 1")]

class Interfaces(models.Model):
    device = models.ForeignKey(Devices,on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=interface_options, default="Fast", blank=False, null=False)
    slot = models.IntegerField(blank=False, choices=slot_options, null=False, default=0)
    port = models.IntegerField(blank=False, choices=port_options, null=False, default=0)
    ip4_address = models.CharField(max_length=16, null=True, default=None)
    status = models.CharField(max_length=4, default="u", choices=status_options, blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['device','type','slot','port'], name="unique slot-port")
        ]

    def __str__(self):
        return f"{self.device} {self.status}"

class Usuarios(models.Model):
    usuario = models.CharField(max_length=20, blank=False, null=False, primary_key=True)
    password = models.CharField(max_length=15, blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['usuario'], name="unique user")
        ]

    def __str__(self):
        return f"{self.usuario}"
       