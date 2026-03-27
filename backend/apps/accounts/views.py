from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, RegisterPublicSerializer, CreateAdminSerializer, CustomTokenSerializer
from .permissions import IsSuperAdmin


class PublicAdminListView(generics.ListAPIView):
    """Liste publique des admins partenaires actifs — pour le formulaire de demande"""
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(role='admin', is_active=True).order_by('organization_name')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = [
            {
                'id': u.id,
                'full_name': u.full_name,
                'organization_name': u.organization_name or u.full_name,
                'partner_type': u.partner_type,
            }
            for u in qs
        ]
        return Response(data)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                from apps.audit.middleware import log_action
                from apps.audit.models import AuditLog
                email = request.data.get('email', '')
                user = User.objects.filter(email=email).first()
                if user:
                    AuditLog.objects.create(
                        user=user, action='LOGIN', level='INFO',
                        description=f"Connexion reussie: {email}",
                        ip_address=request.META.get('REMOTE_ADDR'),
                        endpoint=request.path, method='POST',
                    )
            except Exception:
                pass
        return response


class RegisterPublicView(generics.CreateAPIView):
    serializer_class = RegisterPublicSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        try:
            from apps.audit.models import AuditLog
            AuditLog.objects.create(
                user=user, action='CREATE', level='INFO',
                description=f"Nouveau compte public cree: {user.email}",
                ip_address=self.request.META.get('REMOTE_ADDR'),
                endpoint=self.request.path, method='POST',
            )
        except Exception:
            pass


class CreateAdminView(generics.CreateAPIView):
    serializer_class = CreateAdminSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        admin_user = serializer.save()
        try:
            from apps.audit.middleware import log_action
            log_action(self.request, 'CREATE',
                       f"Admin partenaire cree: {admin_user.email} ({admin_user.partner_type})",
                       obj=admin_user)
        except Exception:
            pass


class ListAdminsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]
    pagination_class = None  # Tous les admins sans pagination

    def get_queryset(self):
        return User.objects.filter(role='admin').order_by('full_name')


class AdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return User.objects.filter(role='admin')


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ToggleAdminStatusView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, pk):
        try:
            admin = User.objects.get(pk=pk, role='admin')
            admin.is_active = not admin.is_active
            admin.save()
            try:
                from apps.audit.middleware import log_action
                action = 'UPDATE'
                desc = f"Admin {admin.email} {'active' if admin.is_active else 'desactive'}"
                log_action(request, action, desc, obj=admin)
            except Exception:
                pass
            return Response({'is_active': admin.is_active})
        except User.DoesNotExist:
            return Response({'error': 'Admin non trouve'}, status=status.HTTP_404_NOT_FOUND)
