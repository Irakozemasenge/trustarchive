from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import AuditLog, SystemError
from .serializers import AuditLogSerializer, SystemErrorSerializer
from apps.accounts.permissions import IsSuperAdmin
from django_filters.rest_framework import DjangoFilterBackend


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['action', 'level', 'user']

    def get_queryset(self):
        qs = AuditLog.objects.all()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class SystemErrorListView(generics.ListAPIView):
    serializer_class = SystemErrorSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['severity', 'resolved', 'error_type']
    queryset = SystemError.objects.all()


class ResolveErrorView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            error = SystemError.objects.get(pk=pk)
            error.resolved = True
            error.resolved_by = request.user
            error.resolved_at = timezone.now()
            error.save()
            return Response({'resolved': True})
        except SystemError.DoesNotExist:
            return Response({'error': 'Introuvable'}, status=404)


class AuditStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response({
            'total_logs': AuditLog.objects.count(),
            'errors_today': AuditLog.objects.filter(level='ERROR', created_at__date=timezone.now().date()).count(),
            'unresolved_errors': SystemError.objects.filter(resolved=False).count(),
            'critical_errors': SystemError.objects.filter(severity='critical', resolved=False).count(),
            'logins_today': AuditLog.objects.filter(action='LOGIN', created_at__date=timezone.now().date()).count(),
            'verifications_today': AuditLog.objects.filter(action='VERIFY', created_at__date=timezone.now().date()).count(),
        })
