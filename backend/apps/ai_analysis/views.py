from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .models import DocumentAnalysis
from .serializers import DocumentAnalysisSerializer
from .service import analyze_document_with_gemma
from apps.accounts.permissions import IsAdminPartner, IsSuperAdmin
from apps.documents.models import Document
import logging

logger = logging.getLogger(__name__)


class AnalyzeDocumentView(APIView):
    """Lance l'analyse IA d'un document"""
    permission_classes = [IsAdminPartner]

    def post(self, request, doc_id):
        try:
            # Vérifier accès au document
            user = request.user
            if user.role == 'superadmin':
                doc = Document.objects.get(pk=doc_id)
            else:
                doc = Document.objects.get(pk=doc_id, issued_by=user)
        except Document.DoesNotExist:
            return Response({'error': 'Document introuvable'}, status=404)

        # Créer ou récupérer l'analyse
        analysis, created = DocumentAnalysis.objects.get_or_create(
            document=doc,
            defaults={'analyzed_by': user, 'status': 'processing'}
        )

        if not created and analysis.status == 'completed':
            # Déjà analysé — retourner le résultat existant
            return Response({
                'cached': True,
                'analysis': DocumentAnalysisSerializer(analysis).data
            })

        # Lancer l'analyse
        analysis.status = 'processing'
        analysis.analyzed_by = user
        analysis.save()

        try:
            summary, key_info, extracted_text, tokens = analyze_document_with_gemma(doc)

            analysis.summary = summary
            analysis.key_information = key_info
            analysis.extracted_text = extracted_text
            analysis.tokens_used = tokens
            analysis.status = 'completed'
            analysis.model_used = key_info.get('mode', 'gemma-3-27b-it')
            analysis.save()

            # Log audit
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    user=user, action='CREATE', level='INFO',
                    description=f"Analyse IA completee pour {doc.unique_number}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    endpoint=request.path, method='POST',
                    extra_data={'tokens': tokens, 'doc': doc.unique_number}
                )
            except Exception:
                pass

            return Response({
                'cached': False,
                'analysis': DocumentAnalysisSerializer(analysis).data
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.save()
            logger.error(f"Analyse IA echouee pour {doc.unique_number}: {e}")
            return Response({'error': f'Analyse echouee: {str(e)}'}, status=500)


class DocumentAnalysisDetailView(APIView):
    """Récupère l'analyse existante d'un document"""
    permission_classes = [IsAdminPartner]

    def get(self, request, doc_id):
        try:
            user = request.user
            if user.role == 'superadmin':
                doc = Document.objects.get(pk=doc_id)
            else:
                doc = Document.objects.get(pk=doc_id, issued_by=user)

            analysis = DocumentAnalysis.objects.get(document=doc)
            return Response(DocumentAnalysisSerializer(analysis).data)
        except Document.DoesNotExist:
            return Response({'error': 'Document introuvable'}, status=404)
        except DocumentAnalysis.DoesNotExist:
            return Response({'error': 'Aucune analyse disponible', 'analyzed': False}, status=404)


class PublicAnalysisView(APIView):
    """Vue publique du résumé IA d'un document (via numéro unique)"""
    permission_classes = [AllowAny]

    def get(self, request, unique_number):
        try:
            doc = Document.objects.get(unique_number=unique_number.upper())
            analysis = DocumentAnalysis.objects.get(document=doc, status='completed')
            return Response({
                'unique_number': doc.unique_number,
                'summary': analysis.summary,
                'key_information': analysis.key_information,
                'analyzed_at': analysis.updated_at,
            })
        except (Document.DoesNotExist, DocumentAnalysis.DoesNotExist):
            return Response({'error': 'Analyse non disponible'}, status=404)


class AIStatsView(APIView):
    """Statistiques des analyses IA"""
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total = DocumentAnalysis.objects.count()
        completed = DocumentAnalysis.objects.filter(status='completed').count()
        failed = DocumentAnalysis.objects.filter(status='failed').count()
        pending = DocumentAnalysis.objects.filter(status='pending').count()
        total_tokens = sum(
            a.tokens_used for a in DocumentAnalysis.objects.filter(status='completed')
        )
        return Response({
            'total_analyses': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'total_tokens_used': total_tokens,
            'success_rate': round((completed / total * 100) if total > 0 else 0, 1),
        })
