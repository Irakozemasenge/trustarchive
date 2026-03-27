from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentCategory, DocumentVerificationLog
from .serializers import (
    DocumentSerializer, PublicDocumentSerializer,
    DocumentCategorySerializer, VerificationLogSerializer
)
from .utils import generate_qr_code
from apps.accounts.permissions import IsAdminPartner, IsSuperAdmin
from apps.blockchain.service import BlockchainService


class PublicVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, unique_number):
        try:
            doc = Document.objects.get(unique_number=unique_number.upper().strip())
            DocumentVerificationLog.objects.create(
                document=doc,
                verified_by_ip=request.META.get('REMOTE_ADDR'),
                verified_by_user=request.user if request.user.is_authenticated else None,
                result=doc.status,
            )
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action='VERIFY', level='INFO',
                    description=f"Verification document: {doc.unique_number} - resultat: {doc.status}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    endpoint=request.path, method='GET',
                    extra_data={'unique_number': doc.unique_number, 'status': doc.status}
                )
            except Exception:
                pass
            serializer = PublicDocumentSerializer(doc, context={'request': request})
            return Response({
                'found': True,
                'authentic': doc.status == 'verified',
                'document': serializer.data
            })
        except Document.DoesNotExist:
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action='VERIFY', level='WARNING',
                    description=f"Tentative verification document introuvable: {unique_number}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    endpoint=request.path, method='GET',
                )
            except Exception:
                pass
            return Response({'found': False, 'authentic': False, 'message': 'Document introuvable'}, status=404)


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminPartner]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'issued_to']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Document.objects.select_related('issued_by', 'category').all()
        return Document.objects.select_related('issued_by', 'category').filter(issued_by=user)

    def perform_create(self, serializer):
        doc = serializer.save(issued_by=self.request.user)
        doc = generate_qr_code(doc)
        doc.save()
        try:
            bc = BlockchainService()
            tx_hash = bc.register_document(doc.unique_number, doc.document_hash)
            doc.blockchain_tx = tx_hash
            doc.save(update_fields=['blockchain_tx'])
        except Exception as e:
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    user=self.request.user, action='ERROR', level='ERROR',
                    description=f"Erreur blockchain pour {doc.unique_number}: {str(e)}",
                    ip_address=self.request.META.get('REMOTE_ADDR'),
                    endpoint=self.request.path, method='POST',
                )
            except Exception:
                pass
        try:
            from apps.audit.middleware import log_action
            log_action(self.request, 'CREATE',
                       f"Document enregistre: {doc.unique_number} - {doc.title} pour {doc.issued_to}",
                       obj=doc)
        except Exception:
            pass


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminPartner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Document.objects.all()
        return Document.objects.filter(issued_by=user)


class RevokeDocumentView(APIView):
    permission_classes = [IsAdminPartner]

    def patch(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
            if request.user.role != 'superadmin' and doc.issued_by != request.user:
                return Response({'error': 'Non autorise'}, status=403)
            doc.status = 'revoked'
            doc.save()
            try:
                from apps.audit.middleware import log_action
                log_action(request, 'REVOKE',
                           f"Document revoque: {doc.unique_number} - {doc.title}",
                           level='WARNING', obj=doc)
            except Exception:
                pass
            return Response({'status': 'revoked'})
        except Document.DoesNotExist:
            return Response({'error': 'Document introuvable'}, status=404)


class DocumentCategoryView(generics.ListCreateAPIView):
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAdminPartner]
    queryset = DocumentCategory.objects.all().order_by('name')
    pagination_class = None  # Toutes les categories sans pagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DocumentCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsSuperAdmin]
    queryset = DocumentCategory.objects.all()
    pagination_class = None


class DocumentStatsView(APIView):
    permission_classes = [IsAdminPartner]

    def get(self, request):
        user = request.user
        qs = Document.objects.all() if user.role == 'superadmin' else Document.objects.filter(issued_by=user)
        return Response({
            'total': qs.count(),
            'verified': qs.filter(status='verified').count(),
            'pending': qs.filter(status='pending').count(),
            'revoked': qs.filter(status='revoked').count(),
            'rejected': qs.filter(status='rejected').count(),
        })


class AllDocumentsSuperAdminView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsSuperAdmin]
    queryset = Document.objects.select_related('issued_by', 'category').all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'issued_by']
