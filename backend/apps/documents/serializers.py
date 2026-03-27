from rest_framework import serializers
from .models import Document, DocumentCategory, DocumentVerificationLog
from apps.accounts.serializers import UserSerializer


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    issued_by_info = UserSerializer(source='issued_by', read_only=True)
    category_info = DocumentCategorySerializer(source='category', read_only=True)
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'unique_number', 'title', 'category', 'category_info',
            'description', 'issued_to', 'issued_to_id', 'issued_date',
            'expiry_date', 'issued_by', 'issued_by_info', 'document_file',
            'qr_code', 'qr_code_url', 'status', 'document_hash',
            'blockchain_tx', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['unique_number', 'document_hash', 'blockchain_tx', 'qr_code', 'issued_by']

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None


class PublicDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour la vérification publique - données limitées"""
    issued_by_org = serializers.CharField(source='issued_by.organization_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'unique_number', 'title', 'category_name', 'issued_to',
            'issued_date', 'expiry_date', 'issued_by_org', 'status',
            'document_hash', 'blockchain_tx', 'qr_code_url', 'created_at'
        ]

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None


class VerificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVerificationLog
        fields = '__all__'
