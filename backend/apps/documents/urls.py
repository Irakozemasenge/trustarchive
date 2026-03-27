from django.urls import path
from .views import (
    PublicVerifyView, DocumentListCreateView, DocumentDetailView,
    RevokeDocumentView, DocumentCategoryView, DocumentCategoryDetailView,
    DocumentStatsView, AllDocumentsSuperAdminView
)

urlpatterns = [
    path('verify/<str:unique_number>/', PublicVerifyView.as_view(), name='verify_document'),
    path('', DocumentListCreateView.as_view(), name='documents'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/revoke/', RevokeDocumentView.as_view(), name='revoke_document'),
    path('categories/', DocumentCategoryView.as_view(), name='categories'),
    path('categories/<int:pk>/', DocumentCategoryDetailView.as_view(), name='category_detail'),
    path('stats/', DocumentStatsView.as_view(), name='stats'),
    path('all/', AllDocumentsSuperAdminView.as_view(), name='all_documents'),
]
