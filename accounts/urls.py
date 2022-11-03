from django.urls import path
from django.views.decorators.csrf import csrf_protect
from accounts.views import SignupView, UniqueIDView, UsersListView, UsersManyToManyView

urlpatterns = [
    path("signup/", csrf_protect(SignupView.as_view())),
    path("related/", UsersListView.as_view()),
    path("<uuid:refer>", UsersManyToManyView.as_view()),
    path("unique_id/", UniqueIDView.as_view())
]