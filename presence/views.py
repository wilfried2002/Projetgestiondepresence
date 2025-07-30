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
        if presence:
            if presence.heure_entree and presence.heure_sortie:
                etat = "Présent"
            else:
                etat = "Absent"
        else:
            etat = "Absent"
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
        presence.heure_entree = now().time()
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
        presence.heure_sortie = now().time()
        presence.save()
        messages.error(request, f"{employee.prenom} {employee.nom} est maintenant sorti.")  # rouge
    else:
        messages.info(request, f"{employee.prenom} {employee.nom} était déjà sorti aujourd'hui.")
    return redirect('tableau_presence')
