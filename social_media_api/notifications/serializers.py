from rest_framework import serializers
from accounts.models import CustomUser
from .models import Notification, NotificationPreference


class ActorSerializer(serializers.ModelSerializer):
    """
    Serializer for the actor (user who performed the action).
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    """
    Main serializer for Notification model.
    """
    actor = ActorSerializer(read_only=True)
    notification_message = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'actor',
            'verb',
            'notification_message',
            'target_type',
            'target_id',
            'is_read',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'recipient',
            'actor',
            'verb',
            'notification_message',
            'target_type',
            'target_id',
            'created_at',
            'updated_at',
        ]
    
    def get_notification_message(self, obj):
        """Get human-readable notification message."""
        return obj.get_notification_message
    
    def get_target_type(self, obj):
        """Get the type of target object."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_target_id(self, obj):
        """Get the ID of target object."""
        return obj.object_id


class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Notification model with full target information.
    """
    actor = ActorSerializer(read_only=True)
    notification_message = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    target_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'actor',
            'verb',
            'notification_message',
            'target_type',
            'target_data',
            'is_read',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
    
    def get_notification_message(self, obj):
        """Get human-readable notification message."""
        return obj.get_notification_message
    
    def get_target_type(self, obj):
        """Get the type of target object."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_target_data(self, obj):
        """Get target object data if available."""
        if obj.target:
            if hasattr(obj.target, 'content'):
                # For Post objects
                return {
                    'id': obj.target.id,
                    'type': obj.content_type.model,
                    'preview': obj.target.content[:100] if hasattr(obj.target, 'content') else ''
                }
            elif hasattr(obj.target, 'text'):
                # For Comment objects
                return {
                    'id': obj.target.id,
                    'type': obj.content_type.model,
                    'preview': obj.target.text[:100] if hasattr(obj.target, 'text') else ''
                }
        return None


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationPreference model.
    """
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'user',
            'notify_on_follow',
            'notify_on_like',
            'notify_on_comment',
            'notify_on_mention',
            'notify_on_reply',
            'email_on_follow',
            'email_on_like',
            'email_on_comment',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list view (minimal data).
    """
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    notification_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'actor_username',
            'verb',
            'notification_message',
            'is_read',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_notification_message(self, obj):
        """Get human-readable notification message."""
        return obj.get_notification_message


class BulkNotificationActionSerializer(serializers.Serializer):
    """
    Serializer for bulk operations on notifications.
    """
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='List of notification IDs to update'
    )
    action = serializers.ChoiceField(
        choices=['mark_read', 'mark_unread', 'delete'],
        help_text='Action to perform on notifications'
    )
    
    def validate_notification_ids(self, value):
        """Validate that IDs are not empty."""
        if not value:
            raise serializers.ValidationError("At least one notification ID must be provided.")
        if any(nid < 1 for nid in value):
            raise serializers.ValidationError("All notification IDs must be positive integers.")
        return value
