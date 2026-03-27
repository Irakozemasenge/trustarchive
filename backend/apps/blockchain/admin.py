from django.contrib import admin
from .models import BlockchainRecord

@admin.register(BlockchainRecord)
class BlockchainAdmin(admin.ModelAdmin):
    list_display = ["block_index", "document_unique_number", "block_hash", "created_at"]
    readonly_fields = ["block_index", "block_hash", "previous_hash", "document_hash", "nonce", "timestamp"]
