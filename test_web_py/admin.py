from django.contrib import admin
from .models import Projet

class Admin(admin.ModelAdmin):
    list_display = ('title', 'description')

admin.site.register(Projet, Admin)