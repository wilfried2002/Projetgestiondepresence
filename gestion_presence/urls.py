"""
URL configuration for gestion_presence project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

from employee.views import generate_badge
import presence
from presence.views import tableau_presence, marquer_entree, marquer_sortie



urlpatterns = [
    path('admin/', admin.site.urls),

    # # Accueil = tableau de présence
    # path('', tableau_presence, name='tableau_presence'),

    # # Marquage entrée/sortie
    # path('entree/<int:employe_id>/', marquer_entree, name='marquer_entree'),
    # path('sortie/<int:employe_id>/', marquer_sortie, name='marquer_sortie'),

    # # Badge PDF
    # path('badge/<int:pk>/', generate_badge, name='generate_badge'),

    # Routes des apps
    path('presence/', include('presence.urls')),
    path('employee/', include('employee.urls')),

    # Redirige la racine vers /presence/tableau/
    path('', RedirectView.as_view(url='/presence/tableau/', permanent=False)),


] 

# URLs pour servir les fichiers statiques et média
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Pour la production, servir les fichiers statiques
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

