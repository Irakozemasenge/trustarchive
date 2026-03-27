from django.urls import path
from .views import AuditLogListView, SystemErrorListView, ResolveErrorView, AuditStatsView

urlpatterns = [
    path('logs/', AuditLogListView.as_view(), name='audit_logs'),
    path('errors/', SystemErrorListView.as_view(), name='system_errors'),
    path('errors/<int:pk>/resolve/', ResolveErrorView.as_view(), name='resolve_error'),
    path('stats/', AuditStatsView.as_view(), name='audit_stats'),
]
