from django.contrib import admin

# Register your models here.

from models import Tabla
from models import Actividad
from models import Like

admin.site.register(Like)
admin.site.register(Tabla)
admin.site.register(Actividad)
