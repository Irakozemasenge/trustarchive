from django.db import models


class BlockchainRecord(models.Model):
    block_index = models.IntegerField(unique=True)
    block_hash = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64)
    document_unique_number = models.CharField(max_length=30)
    document_hash = models.CharField(max_length=64)
    nonce = models.IntegerField(default=0)
    timestamp = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blockchain_records'
        ordering = ['block_index']

    def __str__(self):
        return f"Block #{self.block_index} - {self.document_unique_number}"
