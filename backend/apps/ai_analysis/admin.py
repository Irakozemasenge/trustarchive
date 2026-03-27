from django.contrib import admin
from .models import DocumentAnalysis


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'status', 'model_used', 'tokens_used', 'created_at']
    list_filter = ['status', 'model_used']
    search_fields = ['document__unique_number', 'summary']
    readonly_fields = ['extracted_text', 'summary', 'key_information', 'tokens_used', 'created_at', 'updated_at']
