
from django import template
register = template.Library()
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_presence_by_employee')
def get_presence_by_employee(presences, employee_id):
    """
    Récupère la présence d’un employé à partir d’un dictionnaire ou queryset.
    """
    try:
        # Si c’est un dictionnaire
        if isinstance(presences, dict):
            return presences.get(employee_id)
        # Sinon, si c’est un queryset (ex: Presence.objects.all())
        return presences.get(employee__id=employee_id)
    except Exception:
        return None