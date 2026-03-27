from rest_framework import serializers
from .models import DocumentAnalysis


class DocumentAnalysisSerializer(serializers.ModelSerializer):
    document_number = serializers.CharField(source='document.unique_number', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentAnalysis
        fields = [
            'id', 'document', 'document_number', 'document_title',
            'extracted_text', 'summary', 'key_information',
            'model_used', 'confidence_score', 'status',
            'error_message', 'tokens_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
