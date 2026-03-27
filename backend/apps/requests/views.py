from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DocumentRequest
from .serializers import DocumentRequestSerializer, UpdateRequestSerializer
from apps.accounts.permissions import IsAdminPartner, IsPublicOrAdmin


class MyRequestsView(generics.ListCreateAPIView):
    serializer_class = DocumentRequestSerializer
    permission_classes = [IsPublicOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return DocumentRequest.objects.filter(requester=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class AdminRequestsView(generics.ListAPIView):
    serializer_class = DocumentRequestSerializer
    permission_classes = [IsAdminPartner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return DocumentRequest.objects.all()
        # Un admin voit uniquement les demandes qui lui sont assignées
        # OU les demandes non assignées de son type de partenaire
        return DocumentRequest.objects.filter(assigned_to=user)


class UpdateRequestView(generics.UpdateAPIView):
    serializer_class = UpdateRequestSerializer
    permission_classes = [IsAdminPartner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return DocumentRequest.objects.all()
        # Un admin ne peut modifier que ses propres demandes assignées
        return DocumentRequest.objects.filter(assigned_to=user)


class RequestDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentRequestSerializer
    permission_classes = [IsPublicOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return DocumentRequest.objects.all()
        if user.role == 'admin':
            return DocumentRequest.objects.filter(assigned_to=user)
        return DocumentRequest.objects.filter(requester=user)


class RequestStatsView(APIView):
    permission_classes = [IsAdminPartner]

    def get(self, request):
        user = request.user
        if user.role == 'superadmin':
            qs = DocumentRequest.objects.all()
        else:
            qs = DocumentRequest.objects.filter(assigned_to=user)
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'processing': qs.filter(status='processing').count(),
            'approved': qs.filter(status='approved').count(),
            'rejected': qs.filter(status='rejected').count(),
        })
