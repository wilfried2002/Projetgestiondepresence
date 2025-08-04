from django.db import models
from django.contrib.auth.models import User
from employee.models import Employee
from django.utils import timezone

class Presence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    heure_entree = models.TimeField(null=True, blank=True)
    heure_sortie = models.TimeField(null=True, blank=True)
    remarque = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee__nom']
        verbose_name = "Présence"
        verbose_name_plural = "Présences"

    def __str__(self):
        return f"{self.employee.nom} - {self.date}"

class AgentPointage(models.Model):
    """Modèle pour les agents de pointage avec permissions spécifiques"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_pointage')
    nom_complet = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, unique=True)
    poste = models.CharField(max_length=50, default="Agent de pointage")
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Agent de pointage"
        verbose_name_plural = "Agents de pointage"
        ordering = ['nom_complet']
    
    def __str__(self):
        return f"{self.nom_complet} ({self.matricule})"
    
    def save(self, *args, **kwargs):
        # S'assurer que l'utilisateur a les bonnes permissions
        if not self.user.groups.filter(name='Agents de pointage').exists():
            from django.contrib.auth.models import Group
            group, created = Group.objects.get_or_create(name='Agents de pointage')
            self.user.groups.add(group)
        
        # Donner les permissions nécessaires
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Permissions pour Presence
        presence_ct = ContentType.objects.get_for_model(Presence)
        permissions_presence = Permission.objects.filter(content_type=presence_ct)
        for perm in permissions_presence:
            self.user.user_permissions.add(perm)
        
        # Permissions pour Employee (lecture seule)
        employee_ct = ContentType.objects.get_for_model(Employee)
        employee_permissions = Permission.objects.filter(
            content_type=employee_ct,
            codename__in=['view_employee']
        )
        for perm in employee_permissions:
            self.user.user_permissions.add(perm)
        
        super().save(*args, **kwargs)
