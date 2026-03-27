from django.db import models
from django.conf import settings


class DocumentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]

    TYPE_CHOICES = [
        ('new', 'Nouveau document'),
        ('copy', 'Copie certifiée'),
        ('verification', 'Vérification officielle'),
        ('correction', 'Correction'),
    ]

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_requests')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_requests'
    )
    # Organisation cible choisie par le demandeur
    target_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='targeted_requests',
        help_text="Admin partenaire cible de la demande"
    )
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='new')
    document_title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supporting_file = models.FileField(upload_to='request_files/%Y/%m/', blank=True, null=True)
    admin_notes = models.TextField(blank=True)
    linked_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Demande #{self.id} - {self.document_title}"

    def save(self, *args, **kwargs):
        # Auto-assigner à l'admin cible si pas encore assigné
        if self.target_admin and not self.assigned_to:
            self.assigned_to = self.target_admin
        super().save(*args, **kwargs)
