from django.urls import path
from .views import StudyListView, FileUploadView, StudyProcessingView

urlpatterns = [
    path('upload/', FileUploadView.as_view()),
    path('study/<uuid:unique_id>', StudyProcessingView.as_view()),
    path('studies/', StudyListView.as_view()),
]