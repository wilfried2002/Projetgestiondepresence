from django.urls import path

from presence.views import tableau_presence, marquer_entree, marquer_sortie, fiche_presence_globale, bulletin_paie_temporaire, imprimer_bulletins_temporaire, analyse_presence_globale


urlpatterns = [
    path('tableau/', tableau_presence, name='tableau_presence'),
    path('entree/<int:employe_id>/', marquer_entree, name='marquer_entree'),
    path('sortie/<int:employe_id>/', marquer_sortie, name='marquer_sortie'),
    path('fiche-presence-globale/', fiche_presence_globale, name='fiche_presence_globale'),
    path('bulletin-paie-temporaire/<int:employee_id>/', bulletin_paie_temporaire, name='bulletin_paie_temporaire'),
    path('bulletins-paie-temporaire/', imprimer_bulletins_temporaire, name='imprimer_bulletins_temporaire'),
    path('analyse-presence-globale/', analyse_presence_globale, name='analyse_presence_globale'),
]