from django.shortcuts import get_object_or_404, render
from .models import Employee


# Create your views here.
import io
import qrcode  # type: ignore
from django.http import HttpResponse
from reportlab.pdfgen import canvas  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.lib.utils import ImageReader  # type: ignore
from employee.models import Employee

BADGE_SIZE = (252.0, 153.0)  # ≈ 88.9 mm x 53.9 mm

def generate_badge(request, employee_id):
    try:
        employee = Employee.objects.get(pk=employee_id)
    except Employee.DoesNotExist:
        return HttpResponse("Employé introuvable", status=404)

    qr = qrcode.make(employee.matricule)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_image = ImageReader(qr_buffer)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=badge_{employee.matricule}.pdf'

    c = canvas.Canvas(response, pagesize=BADGE_SIZE)

    # Fond bleu
    c.setFillColorRGB(0.1, 0.3, 0.7)  # Bleu
    c.rect(0, 0, BADGE_SIZE[0], BADGE_SIZE[1], fill=1, stroke=0)

    # Bordure
    c.setLineWidth(2)
    c.setStrokeColorRGB(1, 1, 1)
    c.rect(5, 5, BADGE_SIZE[0] - 10, BADGE_SIZE[1] - 10)

    # Texte employé (en blanc)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(15 * mm, 28 * mm, f"Nom : {employee.nom.upper()}")
    c.drawString(15 * mm, 22 * mm, f"Prénom : {employee.prenom.title()}")
    c.drawString(15 * mm, 16 * mm, f"Poste : {employee.poste.title()}")
    c.drawString(15 * mm, 9 * mm, f"Type : {employee.type.title()}")

    # Photo de l'employé juste au-dessus du QR code
    if employee.photo:
        try:
            photo_path = employee.photo.path
            photo_image = ImageReader(photo_path)
            c.drawImage(
                photo_image,
                BADGE_SIZE[0] - 60, 95,  # juste au-dessus du QR code
                width=40, height=40,
                mask='auto'
            )
        except Exception:
            pass

    # QR code
    c.drawImage(qr_image, BADGE_SIZE[0] - 60, 20, width=40, height=40)

    # Logo Mimosa à l’extrémité droite du badge
    try:
        logo_path = 'd:/AppAccesPersonnelMimosa/static/mimosa_logo.JPG'  # adapte le chemin si besoin
        logo_image = ImageReader(logo_path)
        c.drawImage(
            logo_image,
            BADGE_SIZE[0] - 200, BADGE_SIZE[1] - 55,  # coin supérieur droit
            width=40, height=40,
            mask='auto'
        )
    except Exception:
        pass

    c.showPage()
    c.save()

    return response
