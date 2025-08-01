from django.utils import timezone
from django.shortcuts import redirect, render

# Create your views here.
# views.py dans l'application presence
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from employee.models import Employee
from django.contrib import messages
from presence.models import Presence
from .models import Presence
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt


def tableau_presence(request):
    employee = Employee.objects.filter(actif=True)
    presences = Presence.objects.filter(date=now().date())
    employe_data = []
    for employe in employee:
        presence = presences.filter(employee=employe).first()
        # Par défaut absent
        etat = "(Absent)"
        # Si l'employé est présent
        if presence and presence.heure_entree and presence.heure_sortie:
            etat = "(Etait Présent Aujourd'hui)"
        # Si l'employé est entré mais pas sorti
        elif presence and presence.heure_entree and not presence.heure_sortie:
            etat = "(Entré)"
        # Si l'employé est sorti mais pas entré
        elif presence and presence.heure_sortie and not presence.heure_entree:
            etat = "(Sorti)"
        # Si l'employé n'a pas de présence aujourd'hui
        else:
            etat = "(Absent)"
        employe_data.append({
            "employe": employe,
            "presence": presence,
            "etat_actuel": etat,
        })
    return render(request, "tableau_presence.html", {
        "employe_data": employe_data,
        "messages": messages.get_messages(request),
    })


@csrf_exempt
def marquer_entree(request, employe_id):
    employee = get_object_or_404(Employee, id=employe_id)
    presence, created = Presence.objects.get_or_create(employee=employee, date=now().date())
    if not presence.heure_entree:
        presence.heure_entree = timezone.now().time() # <-- ICI pour l'heure d'entrée
        presence.save()
        messages.success(request, f"{employee.prenom} {employee.nom} est maintenant entré.")  # bleu/vert
    else:
        messages.info(request, f"{employee.prenom} {employee.nom} était déjà entré aujourd'hui.")
    return redirect('tableau_presence')


@csrf_exempt
def marquer_sortie(request, employe_id):
    employee = get_object_or_404(Employee, id=employe_id)
    presence, created = Presence.objects.get_or_create(employee=employee, date=now().date())
    if not presence.heure_sortie:
        presence.heure_sortie = timezone.now().time()  # <-- ICI pour l'heure de sortie
        presence.save()
        messages.error(request, f"{employee.prenom} {employee.nom} est maintenant sorti.")  # rouge
    else:
        messages.info(request, f"{employee.prenom} {employee.nom} était déjà sorti aujourd'hui.")
    return redirect('tableau_presence')


from django.shortcuts import render
from employee.models import Employee
from presence.models import Presence  # à adapter selon ton modèle

def fiche_presence_globale(request):
    import datetime
    import locale
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Pour les noms de jours en français, si supporté
    type_filter = request.GET.get('type')  # 'temporaire', 'permanent', ou None
    employees = Employee.objects.all()
    if type_filter in ['temporaire', 'permanent']:
        employees = employees.filter(type=type_filter)
    data = []
    for emp in employees:
        presences = Presence.objects.filter(employee=emp).order_by('date')
        nb_jours = presences.count()
        salaire_mensuel = emp.salaire_mensuel() if hasattr(emp, 'salaire_mensuel') else "-"
        jours_presence = []
        if emp.type == 'permanent' or type_filter == 'permanent':
            for p in presences:
                # Nom du jour en français, ex: lundi, mardi, etc.
                jour = p.date.strftime('%A')
                jours_presence.append(jour.capitalize())
        data.append({
            'employee': emp,
            'nb_jours': nb_jours,
            'salaire_mensuel': salaire_mensuel,
            'jours_presence': jours_presence,
        })
    return render(request, 'fiche_presence_globale.html', {
        'data': data,
        'type_filter': type_filter,
        'today': datetime.date.today(),
    })


def bulletin_paie_temporaire(request, employee_id):
    import datetime
    from django.shortcuts import get_object_or_404
    employee = get_object_or_404(Employee, id=employee_id, type='temporaire')
    presences = Presence.objects.filter(employee=employee, heure_entree__isnull=False, heure_sortie__isnull=False)
    nb_jours = presences.count()
    montant_mensuel = employee.salaire_mensuel() if hasattr(employee, 'salaire_mensuel') else "-"
    today = datetime.date.today()
    return render(request, 'bulletin_paie_temporaire.html', {
        'employee': employee,
        'nb_jours': nb_jours,
        'montant_mensuel': montant_mensuel,
        'today': today,
    })


def imprimer_bulletins_temporaire(request):
    import datetime
    temporaires = Employee.objects.filter(type='temporaire')
    bulletins = []
    for emp in temporaires:
        presences = Presence.objects.filter(employee=emp, heure_entree__isnull=False, heure_sortie__isnull=False)
        nb_jours = presences.count()
        montant_mensuel = emp.salaire_mensuel() if hasattr(emp, 'salaire_mensuel') else "-"
        bulletins.append({
            'employee': emp,
            'nb_jours': nb_jours,
            'montant_mensuel': montant_mensuel,
        })
    today = datetime.date.today()
    return render(request, 'bulletins_paie_temporaire.html', {
        'bulletins': bulletins,
        'today': today,
    })

def analyse_presence_globale(request):
    import datetime
    from django.db.models import Count, Q
    from django.utils import timezone
    
    # Statistiques globales
    total_employes = Employee.objects.filter(actif=True).count()
    total_temporaires = Employee.objects.filter(actif=True, type='temporaire').count()
    total_permanents = Employee.objects.filter(actif=True, type='permanent').count()
    
    # Présences aujourd'hui
    aujourd_hui = timezone.now().date()
    presences_aujourd_hui = Presence.objects.filter(date=aujourd_hui)
    presents_aujourd_hui = presences_aujourd_hui.filter(heure_entree__isnull=False).count()
    absents_aujourd_hui = total_employes - presents_aujourd_hui
    
    # Statistiques par type
    temporaires_presents = presences_aujourd_hui.filter(
        employee__type='temporaire', 
        heure_entree__isnull=False
    ).count()
    permanents_presents = presences_aujourd_hui.filter(
        employee__type='permanent', 
        heure_entree__isnull=False
    ).count()
    
    # Top des employés les plus présents ce mois
    debut_mois = aujourd_hui.replace(day=1)
    presences_mois = Presence.objects.filter(
        date__gte=debut_mois,
        heure_entree__isnull=False
    ).values('employee__nom', 'employee__prenom').annotate(
        nb_presences=Count('id')
    ).order_by('-nb_presences')[:10]
    
    # Statistiques par service
    stats_service = presences_aujourd_hui.filter(
        heure_entree__isnull=False
    ).values('employee__service').annotate(
        nb_presents=Count('id')
    ).order_by('-nb_presents')
    
    context = {
        'total_employes': total_employes,
        'total_temporaires': total_temporaires,
        'total_permanents': total_permanents,
        'presents_aujourd_hui': presents_aujourd_hui,
        'absents_aujourd_hui': absents_aujourd_hui,
        'temporaires_presents': temporaires_presents,
        'permanents_presents': permanents_presents,
        'presences_mois': presences_mois,
        'stats_service': stats_service,
        'aujourd_hui': aujourd_hui,
        'debut_mois': debut_mois,
    }
    
    return render(request, 'analyse_presence_globale.html', context)

def analyse_financiere(request):
    import datetime
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from calendar import monthrange
    
    # Paramètres de filtrage
    mois = request.GET.get('mois', timezone.now().month)
    annee = request.GET.get('annee', timezone.now().year)
    
    # Date de début et fin du mois
    debut_mois = datetime.date(int(annee), int(mois), 1)
    fin_mois = datetime.date(int(annee), int(mois), monthrange(int(annee), int(mois))[1])
    
    # Statistiques temporaires
    temporaires = Employee.objects.filter(actif=True, type='temporaire')
    presences_temporaires = Presence.objects.filter(
        employee__type='temporaire',
        employee__actif=True,
        date__gte=debut_mois,
        date__lte=fin_mois,
        heure_entree__isnull=False,
        heure_sortie__isnull=False
    )
    
    # Calculs temporaires
    total_temporaires = temporaires.count()
    total_jours_temporaires = presences_temporaires.count()
    cout_temporaires = 0
    
    for temp in temporaires:
        presences_emp = presences_temporaires.filter(employee=temp)
        jours_emp = presences_emp.count()
        if temp.salaire_journalier:
            cout_temporaires += jours_emp * temp.salaire_journalier
    
    # Statistiques permanents
    permanents = Employee.objects.filter(actif=True, type='permanent')
    presences_permanents = Presence.objects.filter(
        employee__type='permanent',
        employee__actif=True,
        date__gte=debut_mois,
        date__lte=fin_mois,
        heure_entree__isnull=False
    )
    
    # Calculs permanents (salaire fixe mensuel)
    total_permanents = permanents.count()
    total_jours_permanents = presences_permanents.count()
    
    # Salaire moyen des permanents (à adapter selon ton modèle)
    salaire_moyen_permanent = 150000  # FCFA par mois (à ajuster)
    cout_permanents = total_permanents * salaire_moyen_permanent
    
    # Totaux
    cout_total = cout_temporaires + cout_permanents
    
    # Détail par employé temporaire
    detail_temporaires = []
    for temp in temporaires:
        presences_emp = presences_temporaires.filter(employee=temp)
        jours_emp = presences_emp.count()
        salaire_emp = jours_emp * (temp.salaire_journalier or 0)
        detail_temporaires.append({
            'employee': temp,
            'jours': jours_emp,
            'salaire_journalier': temp.salaire_journalier or 0,
            'salaire_total': salaire_emp
        })
    
    # Détail par employé permanent
    detail_permanents = []
    for perm in permanents:
        presences_emp = presences_permanents.filter(employee=perm)
        jours_emp = presences_emp.count()
        detail_permanents.append({
            'employee': perm,
            'jours': jours_emp,
            'salaire_mensuel': salaire_moyen_permanent,
            'salaire_total': salaire_moyen_permanent
        })
    
    # Prévisions pour les mois suivants
    mois_suivants = []
    for i in range(1, 4):  # 3 mois suivants
        mois_futur = (int(mois) + i) % 12
        if mois_futur == 0:
            mois_futur = 12
        annee_futur = int(annee) + ((int(mois) + i - 1) // 12)
        
        # Estimation basée sur les données actuelles
        estimation_temporaires = cout_temporaires * 1.05  # +5% par mois
        estimation_permanents = cout_permanents
        estimation_totale = estimation_temporaires + estimation_permanents
        
        mois_suivants.append({
            'mois': mois_futur,
            'annee': annee_futur,
            'nom_mois': datetime.date(annee_futur, mois_futur, 1).strftime('%B %Y'),
            'estimation_temporaires': estimation_temporaires,
            'estimation_permanents': estimation_permanents,
            'estimation_totale': estimation_totale
        })
    
    context = {
        'mois': int(mois),
        'annee': int(annee),
        'nom_mois': debut_mois.strftime('%B %Y'),
        'debut_mois': debut_mois,
        'fin_mois': fin_mois,
        
        # Statistiques temporaires
        'total_temporaires': total_temporaires,
        'total_jours_temporaires': total_jours_temporaires,
        'cout_temporaires': cout_temporaires,
        'detail_temporaires': detail_temporaires,
        
        # Statistiques permanents
        'total_permanents': total_permanents,
        'total_jours_permanents': total_jours_permanents,
        'cout_permanents': cout_permanents,
        'detail_permanents': detail_permanents,
        
        # Totaux
        'cout_total': cout_total,
        
        # Prévisions
        'mois_suivants': mois_suivants,
        
        # Options de filtrage
        'mois_options': [(i, datetime.date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        'annee_options': range(2024, 2027),
    }
    
    return render(request, 'analyse_financiere.html', context)