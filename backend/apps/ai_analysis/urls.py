from django.urls import path
from .views import AnalyzeDocumentView, DocumentAnalysisDetailView, PublicAnalysisView, AIStatsView

urlpatterns = [
    path('analyze/<int:doc_id>/', AnalyzeDocumentView.as_view(), name='analyze_document'),
    path('result/<int:doc_id>/', DocumentAnalysisDetailView.as_view(), name='analysis_result'),
    path('public/<str:unique_number>/', PublicAnalysisView.as_view(), name='public_analysis'),
    path('stats/', AIStatsView.as_view(), name='ai_stats'),
]
