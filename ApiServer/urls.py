"""ApiServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from WebApp.views import *
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/apitest', apitest),
    path('api/v1/devices', devices, name='Devices'),
    path('api/v1/<str:_device>/interfaces', interfaces, name='Interfaces'),
    path('api/v1/<str:_device>/interfaces/<str:_status>', interfaces_status, name='InterStatus'),
    path('devices', process_sub_pag, name='Devices'),
    path('interfaces', process_sub_pag, name='Interfaces'),
    path('usuarios', process_sub_pag, name='Usuarios'),
    path('tokens', process_sub_pag, name='Tokens'),
    path('home', home, name='Home')
]
