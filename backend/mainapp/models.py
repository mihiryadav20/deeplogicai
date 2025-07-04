from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import uuid

# Create your models here.

class UserProfile(models.Model):
    """User profile with role-based access control"""
    
    # Role choices
    ADMIN = 'ADMIN'
    MAINTAINER = 'MAINTAINER'
    REPORTER = 'REPORTER'
    
    ROLE_CHOICES = (
        (ADMIN, _('Admin')),
        (MAINTAINER, _('Maintainer')),
        (REPORTER, _('Reporter')),
    )
    
    # Link to the built-in User model
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Add role field to the profile
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=REPORTER,
        verbose_name=_('Role'),
        help_text=_('Designates the role and permissions of this user.')
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    # Helper methods to check roles
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == self.ADMIN
    
    def is_maintainer(self):
        """Check if user has maintainer role"""
        return self.role == self.MAINTAINER or self.role == self.ADMIN
    
    def is_reporter(self):
        """Check if user has reporter role"""
        return self.role == self.REPORTER


# Signal to create user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Tag(models.Model):
    """Tags for categorizing issues"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Color in hex format (e.g. #007bff)')
    
    def __str__(self):
        return self.name


def issue_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/issues/<issue_id>/<filename>
    return f'issues/{instance.id}/{filename}'

class Issue(models.Model):
    """Issue model for tracking problems and insights"""
    
    # Status workflow
    STATUS_OPEN = 'OPEN'
    STATUS_TRIAGED = 'TRIAGED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_DONE = 'DONE'
    
    STATUS_CHOICES = (
        (STATUS_OPEN, _('Open')),
        (STATUS_TRIAGED, _('Triaged')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_DONE, _('Done')),
    )
    
    # Severity choices
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    SEVERITY_CHOICES = (
        (SEVERITY_LOW, _('Low')),
        (SEVERITY_MEDIUM, _('Medium')),
        (SEVERITY_HIGH, _('High')),
        (SEVERITY_CRITICAL, _('Critical')),
    )
    
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text=_('Markdown supported'))
    attachment = models.FileField(upload_to=issue_upload_path, null=True, blank=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_issues')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_OPEN)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Set the attachment name when saving
        if self.attachment and not self.attachment_name:
            self.attachment_name = self.attachment.name
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validate status transitions
        if self.pk:  # Only check for existing issues
            old_issue = Issue.objects.get(pk=self.pk)
            
            # Define allowed transitions
            allowed_transitions = {
                self.STATUS_OPEN: [self.STATUS_TRIAGED],
                self.STATUS_TRIAGED: [self.STATUS_IN_PROGRESS, self.STATUS_OPEN],
                self.STATUS_IN_PROGRESS: [self.STATUS_DONE, self.STATUS_TRIAGED],
                self.STATUS_DONE: [self.STATUS_IN_PROGRESS],
            }
            
            if old_issue.status != self.status and self.status not in allowed_transitions.get(old_issue.status, []):
                raise ValidationError({
                    'status': f"Cannot transition from '{old_issue.get_status_display()}' to '{self.get_status_display()}'."
                })


class Comment(models.Model):
    """Comments on issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.issue.title}"


class Attachment(models.Model):
    """File attachments for issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='issue_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
