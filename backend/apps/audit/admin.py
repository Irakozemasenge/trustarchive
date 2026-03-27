from django.contrib import admin
from .models import AuditLog, SystemError

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "level", "user", "ip_address", "endpoint", "created_at"]
    list_filter = ["action", "level"]
    search_fields = ["description", "user__email", "ip_address"]
    readonly_fields = [f.name for f in AuditLog._meta.fields]

@admin.register(SystemError)
class SystemErrorAdmin(admin.ModelAdmin):
    list_display = ["error_type", "severity", "resolved", "endpoint", "created_at"]
    list_filter = ["severity", "resolved"]
    search_fields = ["error_type", "message"]
