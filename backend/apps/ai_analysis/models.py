from django.db import models
from django.conf import settings


class DocumentAnalysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Termine'),
        ('failed', 'Echec'),
    ]

    document = models.OneToOneField(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    # Texte extrait du document (OCR)
    extracted_text = models.TextField(blank=True)

    # Résumé généré par Gemma
    summary = models.TextField(blank=True)

    # Informations clés extraites structurées
    key_information = models.JSONField(default=dict, blank=True)

    # Métadonnées de l'analyse
    model_used = models.CharField(max_length=100, default='gemma')
    confidence_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    # Tokens utilisés
    tokens_used = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_analyses'
        verbose_name = 'Analyse IA'

    def __str__(self):
        return f"Analyse IA - {self.document.unique_number} [{self.status}]"
