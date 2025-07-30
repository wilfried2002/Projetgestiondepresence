from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('temporaire', 'Temporaire'),
    ]

    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=EMPLOYEE_TYPE_CHOICES)
    salaire_journalier = models.IntegerField(null=True, blank=True, choices=[(4500, '4500 FCFA'), (5000, '5000 FCFA')])
    
    date_embauche = models.DateField(null=True, blank=True)

    actif = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employee/photos/', blank=True, null=True)  # <- nouveau

    class Meta:
        ordering = ['nom', 'prenom']
        verbose_name = "Employé"
        verbose_name_plural = "Employés"

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    def salaire_mensuel(self):
        if self.type == 'temporaire' and self.salaire_journalier:
            jours_pointes = self.presence_set.filter(heure_entree__isnull=False, heure_sortie__isnull=False).count()
            return self.salaire_journalier * jours_pointes
        return None
