import uuid
import hashlib
from django.db import models
from django.conf import settings


def generate_unique_number():
    """Génère un numéro unique format: TA-YYYY-XXXXXXXX"""
    from django.utils import timezone
    year = timezone.now().year
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"TA-{year}-{unique_id}"


class DocumentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_categories'
        verbose_name = 'Catégorie'

    def __str__(self):
        return self.name


class Document(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('verified', 'Vérifié'),
        ('rejected', 'Rejeté'),
        ('revoked', 'Révoqué'),
    ]

    unique_number = models.CharField(max_length=30, unique=True, default=generate_unique_number)
    title = models.CharField(max_length=300)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    issued_to = models.CharField(max_length=200, help_text="Nom du bénéficiaire")
    issued_to_id = models.CharField(max_length=50, blank=True, help_text="CNI ou passeport")
    issued_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='issued_documents')
    document_file = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='verified')
    document_hash = models.CharField(max_length=64, blank=True)
    blockchain_tx = models.CharField(max_length=100, blank=True, help_text="Hash transaction blockchain")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.unique_number} - {self.title}"

    def compute_hash(self):
        data = f"{self.unique_number}{self.title}{self.issued_to}{self.issued_date}"
        return hashlib.sha256(data.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.document_hash:
            self.document_hash = self.compute_hash()
        super().save(*args, **kwargs)


class DocumentVerificationLog(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='verification_logs')
    verified_by_ip = models.GenericIPAddressField(null=True, blank=True)
    verified_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'document_verification_logs'
