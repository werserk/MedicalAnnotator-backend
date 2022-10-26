from django.urls import path
from .views import FileUploadView, InstanceProcessingView, StudyViewSet, InstanceViewSet

urlpatterns = [
    path('upload/', FileUploadView.as_view()),
    path("instance/<str:dirName>/<str:instanceName>/", InstanceProcessingView.as_view()),
    path("studies/", StudyViewSet.as_view({"get": "list"})),
    path("instances/<str:study>/", InstanceViewSet.as_view({"get": "list"})),
]