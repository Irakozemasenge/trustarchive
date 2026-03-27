from django.contrib import admin
from .models import DocumentRequest

@admin.register(DocumentRequest)
class RequestAdmin(admin.ModelAdmin):
    list_display = ["id", "document_title", "requester", "request_type", "status", "created_at"]
    list_filter = ["status", "request_type"]
    search_fields = ["document_title", "requester__email"]
