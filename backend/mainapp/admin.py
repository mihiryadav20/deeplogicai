from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import UserProfile, Issue, Tag

# User Profile Inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'
    fields = ('role',)

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)
    
    def get_role(self, instance):
        return instance.profile.get_role_display()
    get_role.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Issue Admin
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'severity', 'created_by', 'created_at', 'has_attachment')
    list_filter = ('status', 'severity', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'attachment_name')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status', 'severity')
        }),
        ('Attachment', {
            'fields': ('attachment', 'attachment_name'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Has Attachment'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        # For non-superusers, make all fields read-only after creation
        if obj and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields] + ['attachment']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New issue
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# User Profile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_username', 'get_email', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

# Register remaining models
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Tag)
