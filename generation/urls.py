from django.urls import path
from .views import GenerationView

urlpatterns = [
    path("generate/", GenerationView.as_view())
]