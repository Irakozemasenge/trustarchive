import qrcode
import io
import os
from django.core.files.base import ContentFile
from django.conf import settings


def generate_qr_code(document):
    """Génère un QR code contenant l'URL de vérification du document"""
    verify_url = f"https://trustarchive.bi/verify/{document.unique_number}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e3a5f", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    filename = f"qr_{document.unique_number}.png"
    document.qr_code.save(filename, ContentFile(buffer.read()), save=False)
    return document
