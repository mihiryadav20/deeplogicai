from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, Issue


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    role = serializers.CharField(source='profile.get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    
    def validate_email(self, value):
        """Validate that email belongs to deeplogicai.tech domain"""
        if not value.endswith('@deeplogicai.tech'):
            raise serializers.ValidationError(
                'Only deeplogicai.tech email addresses are allowed.',
                code='invalid_domain'
            )
        return value
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            # Check if user has the required role
            if not hasattr(user, 'profile') or not user.profile.is_maintainer():
                msg = 'Only maintainers and admins can log in.'
                raise serializers.ValidationError(msg, code='authorization')
            
            # Authenticate with username and password
            user = authenticate(request=self.context.get('request'),
                               username=user.username,
                               password=password)
            
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class IssueSerializer(serializers.ModelSerializer):
    """Serializer for the Issue model"""
    created_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = Issue
        fields = ('id', 'title', 'description', 'status', 'status_display', 
                  'severity', 'severity_display', 'created_by', 'created_at', 
                  'updated_at', 'attachment', 'attachment_name')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'attachment_name')
