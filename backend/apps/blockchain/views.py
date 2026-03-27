from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import BlockchainRecord
from .service import BlockchainService
from apps.accounts.permissions import IsSuperAdmin
from rest_framework import serializers


class BlockchainRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainRecord
        fields = '__all__'


class VerifyChainView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        bc = BlockchainService()
        valid, message = bc.verify_chain()
        return Response({'valid': valid, 'message': message})


class BlockchainRecordsView(generics.ListAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = BlockchainRecordSerializer
    queryset = BlockchainRecord.objects.all()


class PublicVerifyHashView(APIView):
    """Vérification publique d'un document via son hash blockchain"""
    permission_classes = [AllowAny]

    def post(self, request):
        unique_number = request.data.get('unique_number')
        document_hash = request.data.get('document_hash')
        if not unique_number or not document_hash:
            return Response({'error': 'unique_number et document_hash requis'}, status=400)
        bc = BlockchainService()
        is_valid = bc.verify_document(unique_number, document_hash)
        return Response({'authentic': is_valid})
