from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomUser
from posts.models import Like, Comment, Post
from .models import Notification, NotificationPreference


@receiver(post_save, sender=CustomUser)
def user_followed_signal(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a user is followed.
    
    This signal is triggered when a CustomUser instance is saved.
    However, we use the m2m_changed signal for the followers relationship
    to truly detect when a follow happens.
    """
    pass


@receiver(post_save, sender=Like)
def like_created_signal(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a post is liked.
    
    When a user likes a post, notify the post's author
    (unless they liked their own post).
    """
    if created:
        # Don't notify if user likes their own post
        if instance.user != instance.post.author:
            # Check if recipient has notification preference enabled
            try:
                preference = NotificationPreference.objects.get(
                    user=instance.post.author
                )
                if not preference.like_notifications:
                    return
            except NotificationPreference.DoesNotExist:
                # Create default preferences if they don't exist
                NotificationPreference.objects.create(user=instance.post.author)
            
            # Create the notification
            Notification.objects.create(
                recipient=instance.post.author,
                actor=instance.user,
                verb='like',
                content_type=ContentType.objects.get_for_model(Post),
                object_id=instance.post.id
            )


@receiver(post_save, sender=Comment)
def comment_created_signal(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a post is commented on.
    
    When a user comments on a post, notify:
    1. The post's author (unless they commented on their own post)
    2. Other commenters on the same post (optional - for replies)
    """
    if created:
        # Notify post author if not their own comment
        if instance.post.author != instance.author:
            # Check preference
            try:
                preference = NotificationPreference.objects.get(
                    user=instance.post.author
                )
                if not preference.comment_notifications:
                    return
            except NotificationPreference.DoesNotExist:
                NotificationPreference.objects.create(user=instance.post.author)
            
            # Create notification
            Notification.objects.create(
                recipient=instance.post.author,
                actor=instance.author,
                verb='comment',
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=instance.id
            )
        
        # Notify other commenters if parent_comment exists (reply detection)
        if instance.parent_comment:
            parent_author = instance.parent_comment.author
            
            # Don't notify if replying to own comment
            if parent_author != instance.author:
                try:
                    preference = NotificationPreference.objects.get(
                        user=parent_author
                    )
                    if not preference.reply_notifications:
                        return
                except NotificationPreference.DoesNotExist:
                    NotificationPreference.objects.create(user=parent_author)
                
                # Create reply notification
                Notification.objects.create(
                    recipient=parent_author,
                    actor=instance.author,
                    verb='reply',
                    content_type=ContentType.objects.get_for_model(Comment),
                    object_id=instance.id
                )


def create_follow_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Signal to create notification when user is followed.
    
    This signal connects to the m2m_changed signal for the followers relationship.
    """
    if action == 'post_add':
        # instance is the user being followed
        # pk_set contains the IDs of users doing the following
        
        for follower_id in pk_set:
            follower = CustomUser.objects.get(id=follower_id)
            
            # Check if the followed user has follow notifications enabled
            try:
                preference = NotificationPreference.objects.get(
                    user=instance
                )
                if not preference.follow_notifications:
                    continue
            except NotificationPreference.DoesNotExist:
                NotificationPreference.objects.create(user=instance)
            
            # Create the notification
            Notification.objects.create(
                recipient=instance,
                actor=follower,
                verb='follow',
            )


# Import at the end to avoid circular imports
from django.db.models.signals import m2m_changed
from .apps import NotificationsConfig

# Connect the m2m_changed signal for followers
CustomUser.followers.through.m2m_changed.connect(
    create_follow_notification,
    sender=CustomUser.followers.through,
    weak=False
)
