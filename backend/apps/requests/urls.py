from django.urls import path
from .views import MyRequestsView, AdminRequestsView, UpdateRequestView, RequestDetailView, RequestStatsView

urlpatterns = [
    path('', MyRequestsView.as_view(), name='my_requests'),
    path('admin/', AdminRequestsView.as_view(), name='admin_requests'),
    path('<int:pk>/', RequestDetailView.as_view(), name='request_detail'),
    path('<int:pk>/update/', UpdateRequestView.as_view(), name='update_request'),
    path('stats/', RequestStatsView.as_view(), name='request_stats'),
]
