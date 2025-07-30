from django.urls import path

from presence.views import tableau_presence, marquer_entree, marquer_sortie


urlpatterns = [
    path('tableau/', tableau_presence, name='tableau_presence'),
    path('entree/<int:employe_id>/', marquer_entree, name='marquer_entree'),
    path('sortie/<int:employe_id>/', marquer_sortie, name='marquer_sortie'),
]