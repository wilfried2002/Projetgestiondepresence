from django.urls import path
from .views import generate_badge

urlpatterns = [
    path('badge/<int:employee_id>/', generate_badge, name='generate_badge'),


    
]