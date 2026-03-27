from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterPublicView, CreateAdminView,
    ListAdminsView, AdminDetailView, MeView, ToggleAdminStatusView,
    PublicAdminListView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterPublicView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('admins/', ListAdminsView.as_view(), name='list_admins'),
    path('admins/create/', CreateAdminView.as_view(), name='create_admin'),
    path('admins/<int:pk>/', AdminDetailView.as_view(), name='admin_detail'),
    path('admins/<int:pk>/toggle/', ToggleAdminStatusView.as_view(), name='toggle_admin'),
    path('partners/', PublicAdminListView.as_view(), name='public_partners'),
]
