from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Creation'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('VIEW', 'Consultation'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Deconnexion'),
        ('VERIFY', 'Verification document'),
        ('REVOKE', 'Revocation document'),
        ('REGISTER_BLOCKCHAIN', 'Enregistrement blockchain'),
        ('REQUEST_SUBMIT', 'Soumission demande'),
        ('REQUEST_UPDATE', 'Mise a jour demande'),
        ('ERROR', 'Erreur systeme'),
    ]
    LEVEL_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('ERROR', 'Erreur'),
        ('CRITICAL', 'Critique'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    endpoint = models.CharField(max_length=300, blank=True)
    method = models.CharField(max_length=10, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        verbose_name = 'Journal audit'

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonyme'
        return f"[{self.level}] {self.action} par {user_str}"


class SystemError(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Eleve'),
        ('critical', 'Critique'),
    ]

    error_type = models.CharField(max_length=100)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    endpoint = models.CharField(max_length=300, blank=True)
    method = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reported_errors'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_errors'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_errors'
        ordering = ['-created_at']
        verbose_name = 'Erreur systeme'

    def __str__(self):
        return f"[{self.severity.upper()}] {self.error_type}"
