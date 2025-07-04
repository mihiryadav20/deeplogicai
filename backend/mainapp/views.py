from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Issue, UserProfile
from .serializers import UserSerializer, LoginSerializer, IssueSerializer
from .permissions import IsAdmin, IsMaintainer


class LoginView(APIView):
    """View for user login with email and password"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data and token
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class UserDetailView(generics.RetrieveAPIView):
    """View to retrieve user details"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    serializer_class = IssueSerializer
    permission_classes = [IsMaintainer]
    
    def get_queryset(self):
        return Issue.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
