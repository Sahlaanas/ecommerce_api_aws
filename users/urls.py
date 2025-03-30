from django.urls import path
from .views import RegisterView, LoginView, ProtectedView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protect/', ProtectedView.as_view(), name='protect')
]
