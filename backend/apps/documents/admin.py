from django.contrib import admin
from .models import Document, DocumentCategory, DocumentVerificationLog

@admin.register(DocumentCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["unique_number", "title", "issued_to", "status", "issued_by", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["unique_number", "title", "issued_to"]
    readonly_fields = ["unique_number", "document_hash", "blockchain_tx", "qr_code"]

@admin.register(DocumentVerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ["document", "verified_at", "result", "verified_by_ip"]
