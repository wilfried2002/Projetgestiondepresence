from django.contrib import admin, messages


# Register your models here.
from django import forms
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
from .models import Employee
import openpyxl



# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = ('matricule', 'nom', 'prenom', 'poste', 'type', 'actif')
#     search_fields = ('nom', 'prenom', 'matricule')
#     list_filter = ('type', 'service', 'actif')
#     ordering = ('nom', 'prenom')
#     list_per_page = 20

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Fichier Excel (.xlsx)")

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'matricule', 'nom', 'prenom', 'poste', 'type', 'actif',
        'photo_display',  # Ajoute cette ligne
        'badge_link', 'salaire_journalier', 'salaire_mensuel_display'
    )
    search_fields = ('nom', 'prenom', 'matricule')
    list_filter = ('type', 'service', 'actif')
    ordering = ('nom', 'prenom')
    list_per_page = 20
    change_list_template = "admin/employee_import.html"
    
    def photo_display(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:50%;" />', obj.photo.url)
        return format_html('<span style="display:inline-block;width:40px;height:40px;background:#eee;border-radius:50%;text-align:center;line-height:40px;">?</span>')
    photo_display.short_description = "Photo"

    def badge_link(self, obj):
        return format_html(
            '<a class="button" href="/employee/badge/{}/" target="_blank">🎫badge</a>', obj.id
        )
    badge_link.short_description = 'Badge'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-employes/', self.import_employees),
            path('fiche-presence-globale/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/fiche-presence-globale/')),
                 name='fiche_presence_globale'),
        ]
        return custom_urls + urls

    def import_employees(self, request):
        if request.method == "POST":
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                wb = openpyxl.load_workbook(form.cleaned_data['excel_file'])
                ws = wb.active

                lignes_importees = 0

                for row in ws.iter_rows(min_row=2, values_only=True):  # En supposant que la 1ère ligne est l'entête
                    matricule, nom, prenom, poste, service, type_emp, date_embauche = row
                    if not Employee.objects.filter(matricule=matricule).exists():
                        Employee.objects.create(
                            matricule=matricule,
                            nom=nom,
                            prenom=prenom,
                            poste=poste,
                            service=service,
                            type= str(type_emp).strip().lower(),
                            date_embauche=date_embauche
                        )
                        lignes_importees += 1

                self.message_user(request, f"{lignes_importees} employés importés avec succès.", messages.SUCCESS)
                return redirect("..")
        else:
            form = ExcelImportForm()

        context = {
            'form': form,
            'title': 'Importer des employés depuis Excel',
        }
        return render(request, "admin/employee_excel_form.html", context)
    
    
    

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.type == 'temporaire':
            form.base_fields['salaire_journalier'].widget = admin.widgets.AdminTextInputWidget()
        
            
        return form

    def salaire_mensuel_display(self, obj):
        if obj.type == 'temporaire':
            return f"{obj.salaire_mensuel()} FCFA"
        return "-"
    salaire_mensuel_display.short_description = "Salaire Mensuel"

    class Media:
        js = ('employee/admin_employee.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-employes/', self.import_employees),
            path('fiche-presence-globale/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/fiche-presence-globale/')),
                 name='fiche_presence_globale'),
            path('liste-presence-tous/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/fiche-presence-globale/')),
                 name='liste_presence_tous'),
            path('liste-presence-temporaires/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/fiche-presence-globale/?type=temporaire')),
                 name='liste_presence_temporaires'),
            path('liste-presence-permanents/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/fiche-presence-globale/?type=permanent')),
                 name='liste_presence_permanents'),
            path('analyse-presence-globale/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/analyse-presence-globale/')),
                 name='analyse_presence_globale'),
            path('analyse-financiere/', 
                 self.admin_site.admin_view(lambda request: redirect('/presence/analyse-financiere/')),
                 name='analyse_financiere'),
        ]
        return custom_urls + urls