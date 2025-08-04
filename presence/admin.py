from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Presence, AgentPointage

class AgentPointageAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'matricule', 'user', 'poste', 'actif', 'date_creation', 'derniere_connexion')
    list_filter = ('actif', 'poste', 'date_creation')
    search_fields = ('nom_complet', 'matricule', 'user__username')
    readonly_fields = ('date_creation', 'derniere_connexion')
    ordering = ('nom_complet',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'nom_complet', 'matricule', 'poste')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
        ('Informations système', {
            'fields': ('date_creation', 'derniere_connexion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nouvel agent
            # Créer un utilisateur si nécessaire
            if not obj.user:
                # Générer un nom d'utilisateur basé sur le matricule
                username = f"agent_{obj.matricule.lower()}"
                # Générer un mot de passe temporaire
                import random
                import string
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                user = User.objects.create_user(
                    username=username,
                    password=temp_password,
                    first_name=obj.nom_complet.split()[0] if obj.nom_complet else '',
                    last_name=' '.join(obj.nom_complet.split()[1:]) if len(obj.nom_complet.split()) > 1 else ''
                )
                obj.user = user
                
                # Afficher le mot de passe temporaire
                from django.contrib import messages
                messages.warning(
                    request, 
                    f"Compte créé pour {obj.nom_complet}. "
                    f"Nom d'utilisateur: {username}, "
                    f"Mot de passe temporaire: {temp_password}. "
                    "L'agent devra changer son mot de passe lors de sa première connexion."
                )
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression d'agents actifs
        if obj and obj.actif:
            return False
        return super().has_delete_permission(request, obj)

class PresenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'heure_entree', 'heure_sortie', 'statut_presence')
    list_filter = ('date', 'employee__type', 'employee__actif')
    search_fields = ('employee__nom', 'employee__prenom', 'employee__matricule')
    date_hierarchy = 'date'
    ordering = ('-date', 'employee__nom')
    
    def statut_presence(self, obj):
        if obj.heure_entree and obj.heure_sortie:
            return "Présent"
        elif obj.heure_entree:
            return "Entré"
        elif obj.heure_sortie:
            return "Sorti"
        else:
            return "Absent"
    statut_presence.short_description = "Statut"

# Enregistrer les modèles
admin.site.register(Presence, PresenceAdmin)
admin.site.register(AgentPointage, AgentPointageAdmin)

# Personnaliser l'admin pour les utilisateurs
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# Désenregistrer et réenregistrer User avec l'admin personnalisé
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)