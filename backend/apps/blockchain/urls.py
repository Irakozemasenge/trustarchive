from django.urls import path
from .views import VerifyChainView, BlockchainRecordsView, PublicVerifyHashView

urlpatterns = [
    path('verify-chain/', VerifyChainView.as_view(), name='verify_chain'),
    path('records/', BlockchainRecordsView.as_view(), name='blockchain_records'),
    path('verify-hash/', PublicVerifyHashView.as_view(), name='verify_hash'),
]
