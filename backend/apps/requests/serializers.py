from rest_framework import serializers
from .models import DocumentRequest
from apps.accounts.serializers import UserSerializer
from apps.documents.serializers import DocumentSerializer


class DocumentRequestSerializer(serializers.ModelSerializer):
    requester_info = UserSerializer(source='requester', read_only=True)
    assigned_to_info = UserSerializer(source='assigned_to', read_only=True)
    target_admin_info = UserSerializer(source='target_admin', read_only=True)
    linked_document_info = DocumentSerializer(source='linked_document', read_only=True)

    class Meta:
        model = DocumentRequest
        fields = [
            'id', 'requester', 'requester_info', 'assigned_to', 'assigned_to_info',
            'target_admin', 'target_admin_info',
            'request_type', 'document_title', 'description', 'status',
            'supporting_file', 'admin_notes', 'linked_document', 'linked_document_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['requester', 'status', 'admin_notes', 'linked_document', 'assigned_to']


class UpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = ['status', 'admin_notes', 'assigned_to', 'linked_document']
