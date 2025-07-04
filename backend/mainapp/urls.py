from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'issues', views.IssueViewSet, basename='issue')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/user/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Include router URLs
    path('', include(router.urls)),
]
