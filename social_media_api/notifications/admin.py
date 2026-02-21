from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ('id', 'recipient', 'actor', 'verb', 'is_read', 'created_at')
    list_filter = ('verb', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'actor__email', 'recipient__username', 'actor__username')
    readonly_fields = ('created_at', 'updated_at', 'content_type', 'object_id')
    fieldsets = (
        ('Notification Info', {
            'fields': ('recipient', 'actor', 'verb', 'is_read')
        }),
        ('Related Content', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Don't allow editing notification recipients or actors."""
        if obj:
            return self.readonly_fields + ('recipient', 'actor', 'verb')
        return self.readonly_fields


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model."""
    list_display = ('user', 'follow_notifications', 'like_notifications', 'comment_notifications')
    list_filter = ('follow_notifications', 'like_notifications', 'comment_notifications', 'reply_notifications', 'mention_notifications')
    search_fields = ('user__email', 'user__username')
    
    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Notification Preferences', {
            'fields': (
                'follow_notifications',
                'like_notifications',
                'comment_notifications',
                'mention_notifications',
                'reply_notifications',
            ),
            'description': 'Enable or disable notifications for each type of activity.',
        }),
        ('Email Preferences', {
            'fields': (
                'email_on_follow',
                'email_on_like',
                'email_on_comment',
            ),
            'description': 'Receive email notifications for selected activities.',
            'classes': ('collapse',),
        }),
    )
