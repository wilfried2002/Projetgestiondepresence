from django.db import models

# Create your models here.
from django.db import models
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
