from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import CustomUser


class Notification(models.Model):
    """
    Notification model for tracking user activities.
    
    This model tracks important activities such as:
    - New followers
    - Likes on posts
    - Comments on posts
    - Replies to comments
    """
    
    # Choices for notification types
    NOTIFICATION_TYPES = (
        ('follow', 'New Follower'),
        ('like', 'Post Liked'),
        ('comment', 'Post Commented'),
        ('mention', 'User Mentioned'),
        ('reply', 'Comment Reply'),
    )
    
    # Recipient of the notification
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User receiving the notification'
    )
    
    # Actor performing the action
    actor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='actions',
        help_text='User performing the action'
    )
    
    # Type of notification
    verb = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        help_text='Type of activity that triggered notification'
    )
    
    # Generic relation to any model (Post, Comment, etc)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    target = GenericForeignKey('content_type', 'object_id')
    
    # Read status
    is_read = models.BooleanField(
        default=False,
        help_text='Whether the recipient has read this notification'
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the notification was created'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the notification was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When the notification was last updated'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        """String representation of notification."""
        action_map = {
            'follow': 'followed you',
            'like': 'liked your post',
            'comment': 'commented on your post',
            'mention': 'mentioned you',
            'reply': 'replied to your comment',
        }
        action = action_map.get(self.verb, 'interacted with you')
        return f'{self.actor.username} {action}'
    
    @property
    def get_notification_message(self):
        """Generate a human-readable notification message."""
        actor_name = self.actor.username
        
        message_map = {
            'follow': f'{actor_name} started following you',
            'like': f'{actor_name} liked your post',
            'comment': f'{actor_name} commented on your post',
            'mention': f'{actor_name} mentioned you',
            'reply': f'{actor_name} replied to your comment',
        }
        return message_map.get(self.verb, f'{actor_name} interacted with you')
    
    @property
    def get_related_object_url(self):
        """Get URL to the object being acted upon."""
        if self.target:
            if hasattr(self.target, 'get_absolute_url'):
                return self.target.get_absolute_url()
        return None


class NotificationPreference(models.Model):
    """
    User preferences for notifications.
    Allows users to control which notifications they receive.
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Notification type preferences
    notify_on_follow = models.BooleanField(
        default=True,
        help_text='Receive notifications when someone follows you'
    )
    notify_on_like = models.BooleanField(
        default=True,
        help_text='Receive notifications when someone likes your post'
    )
    notify_on_comment = models.BooleanField(
        default=True,
        help_text='Receive notifications when someone comments on your post'
    )
    notify_on_mention = models.BooleanField(
        default=True,
        help_text='Receive notifications when someone mentions you'
    )
    notify_on_reply = models.BooleanField(
        default=True,
        help_text='Receive notifications when someone replies to your comment'
    )
    
    # Email notification preferences
    email_on_follow = models.BooleanField(
        default=False,
        help_text='Email notifications for new followers'
    )
    email_on_like = models.BooleanField(
        default=False,
        help_text='Email notifications for post likes'
    )
    email_on_comment = models.BooleanField(
        default=False,
        help_text='Email notifications for post comments'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        """String representation."""
        return f'Notification preferences for {self.user.username}'
