from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Presence

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'heure_entree', 'heure_sortie')
    list_filter = ('date', 'employee__type')
    search_fields = ('employee__nom', 'employee__matricule')
    ordering = ('-date', 'employee__nom')
    list_per_page = 20