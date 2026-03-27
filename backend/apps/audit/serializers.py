from rest_framework import serializers
from .models import AuditLog, SystemError


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default='Anonyme')
    user_name = serializers.CharField(source='user.full_name', read_only=True, default='')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'action', 'level',
            'description', 'ip_address', 'endpoint', 'method',
            'status_code', 'extra_data', 'created_at'
        ]


class SystemErrorSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default='Anonyme')

    class Meta:
        model = SystemError
        fields = [
            'id', 'error_type', 'message', 'traceback', 'endpoint',
            'method', 'user', 'user_email', 'ip_address', 'severity',
            'resolved', 'resolved_by', 'resolved_at', 'created_at'
        ]
