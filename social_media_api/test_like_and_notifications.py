"""
Test suite for Like functionality and Notification system integration.
Tests ensure that:
1. Users can like/unlike posts without duplicate likes
2. Notifications are created automatically when posts are liked
3. User preferences are respected when creating notifications
4. All edge cases are handled properly
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from posts.models import Post, Like, Comment
from notifications.models import Notification, NotificationPreference

User = get_user_model()


class LikeFunctionalityTests(TestCase):
    """Tests for the Like model and like/unlike operations."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create test post
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content'
        )
    
    def test_like_post_creates_like_object(self):
        """Test that liking a post creates a Like object."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(self.post.likes.count(), 1)
        self.assertTrue(self.post.likes.filter(user=self.user2).exists())
    
    def test_cannot_like_post_twice(self):
        """Test that a user cannot like the same post twice."""
        self.client.force_authenticate(user=self.user2)
        
        # First like should succeed
        response1 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second like should fail
        response2 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already liked', response2.data['error'].lower())
        self.assertEqual(Like.objects.count(), 1)
    
    def test_unlike_post_removes_like(self):
        """Test that unliking a post removes the Like object."""
        self.client.force_authenticate(user=self.user2)
        
        # Create a like
        Like.objects.create(user=self.user2, post=self.post)
        self.assertEqual(self.post.likes.count(), 1)
        
        # Unlike the post
        response = self.client.post(f'/api/posts/{self.post.id}/unlike/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)
        self.assertEqual(self.post.likes.count(), 0)
    
    def test_cannot_unlike_post_not_liked(self):
        """Test that user cannot unlike a post they haven't liked."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(f'/api/posts/{self.post.id}/unlike/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not liked', response.data['error'].lower())
    
    def test_like_count_is_accurate(self):
        """Test that like count is accurately reported."""
        self.client.force_authenticate(user=self.user2)
        
        # Like the post
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.data['likes_count'], 1)
        
        # Unlike the post
        response = self.client.post(f'/api/posts/{self.post.id}/unlike/')
        self.assertEqual(response.data['likes_count'], 0)
    
    def test_multiple_users_can_like_same_post(self):
        """Test that multiple users can like the same post."""
        user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # User2 likes post
        self.client.force_authenticate(user=self.user2)
        response1 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # User3 likes post
        self.client.force_authenticate(user=user3)
        response2 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(self.post.likes.count(), 2)
    
    def test_cannot_like_own_post_notification_skip(self):
        """Test that user can like their own post but notification is skipped."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        
        # Like should create successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.post.likes.count(), 1)
        
        # But no notification should be created (user1 is the author)
        # This is handled by the signal handler
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.user1,
                actor=self.user1,
                verb='like'
            ).count(),
            0
        )


class LikeNotificationIntegrationTests(TestCase):
    """Tests for Like functionality triggering Notification creation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create notification preferences with defaults
        self.pref1 = NotificationPreference.objects.create(user=self.user1)
        self.pref2 = NotificationPreference.objects.create(user=self.user2)
        
        # Create test post
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content'
        )
    
    def test_like_creates_notification_for_post_author(self):
        """Test that liking a post creates a notification for the post author."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that notification was created
        notifications = Notification.objects.filter(
            recipient=self.user1,
            actor=self.user2,
            verb='like'
        )
        self.assertEqual(notifications.count(), 1)
        
        notification = notifications.first()
        self.assertEqual(notification.target, self.post)
    
    def test_notification_respects_user_preference_disabled(self):
        """Test that notification is not created if user has disabled like notifications."""
        # Disable like notifications for user1
        self.pref1.like_notifications = False
        self.pref1.save()
        
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that NO notification was created
        notifications = Notification.objects.filter(
            recipient=self.user1,
            actor=self.user2,
            verb='like'
        )
        self.assertEqual(notifications.count(), 0)
    
    def test_notification_respects_user_preference_enabled(self):
        """Test that notification is created when user preference is enabled."""
        # Ensure like notifications are enabled for user1
        self.pref1.like_notifications = True
        self.pref1.save()
        
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that notification was created
        notifications = Notification.objects.filter(
            recipient=self.user1,
            actor=self.user2,
            verb='like'
        )
        self.assertEqual(notifications.count(), 1)


class CommentNotificationIntegrationTests(TestCase):
    """Tests for Comment functionality triggering Notification creation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        # Create notification preferences
        self.pref1 = NotificationPreference.objects.create(user=self.user1)
        self.pref2 = NotificationPreference.objects.create(user=self.user2)
        self.pref3 = NotificationPreference.objects.create(user=self.user3)
        
        # Create test post
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post content'
        )
    
    def test_comment_creates_notification_for_post_author(self):
        """Test that commenting on a post creates a notification for the author."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post(
            f'/api/posts/{self.post.id}/comment/',
            {'content': 'Test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that notification was created
        notifications = Notification.objects.filter(
            recipient=self.user1,
            actor=self.user2,
            verb='comment'
        )
        self.assertEqual(notifications.count(), 1)
    
    def test_reply_to_comment_creates_notification_for_commenter(self):
        """Test that replying to a comment creates a notification for the original commenter."""
        # User2 comments on post
        comment = Comment.objects.create(
            author=self.user2,
            post=self.post,
            content='Original comment'
        )
        
        # User3 replies to User2's comment
        self.client.force_authenticate(user=self.user3)
        
        response = self.client.post(
            f'/api/posts/{self.post.id}/comment/',
            {
                'content': 'Reply to comment',
                'parent_comment': comment.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that reply notification was created for user2
        notifications = Notification.objects.filter(
            recipient=self.user2,
            actor=self.user3,
            verb='reply'
        )
        self.assertEqual(notifications.count(), 1)
    
    def test_nested_comments_structure(self):
        """Test that nested comments are properly structured."""
        # User2 comments
        comment1 = Comment.objects.create(
            author=self.user2,
            post=self.post,
            content='First comment'
        )
        
        # User3 replies
        comment2 = Comment.objects.create(
            author=self.user3,
            post=self.post,
            content='Reply to first',
            parent_comment=comment1
        )
        
        # Verify structure
        self.assertTrue(comment1.is_reply() == False)
        self.assertTrue(comment2.is_reply() == True)
        self.assertEqual(comment2.parent_comment, comment1)
        self.assertEqual(comment1.get_reply_count(), 1)


class NotificationPreferenceTests(TestCase):
    """Tests for notification preferences."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_get_preferences_creates_default(self):
        """Test that getting preferences creates default settings if they don't exist."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/preferences/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['follow_notifications'])
        self.assertTrue(response.data['like_notifications'])
    
    def test_update_preferences(self):
        """Test that preferences can be updated."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(
            '/api/preferences/',
            {
                'like_notifications': False,
                'comment_notifications': False
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify preferences were updated
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertFalse(pref.like_notifications)
        self.assertFalse(pref.comment_notifications)
        self.assertTrue(pref.follow_notifications)  # Should be unchanged


class NotificationRetrievalTests(TestCase):
    """Tests for retrieving notifications via API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create notifications
        self.notif1 = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb='like'
        )
        self.notif2 = Notification.objects.create(
            recipient=self.user1,
            actor=self.user2,
            verb='follow',
            is_read=True
        )
    
    def test_list_notifications(self):
        """Test listing notifications for authenticated user."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_unread_notifications(self):
        """Test filtering notifications by read status."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/notifications/?unread=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.notif1.id)
    
    def test_get_unread_count(self):
        """Test getting unread notification count."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/notifications/unread_count/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
    
    def test_mark_notification_read(self):
        """Test marking a notification as read."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(f'/api/notifications/{self.notif1.id}/mark_read/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify notification was marked as read
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
    
    def test_mark_all_read(self):
        """Test marking all notifications as read."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post('/api/notifications/mark_all_read/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Verify all notifications are read
        unread = Notification.objects.filter(
            recipient=self.user1,
            is_read=False
        )
        self.assertEqual(unread.count(), 0)
    
    def test_bulk_action_mark_read(self):
        """Test bulk marking notifications as read."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(
            '/api/notifications/bulk_action/',
            {
                'notification_ids': [self.notif1.id, self.notif2.id],
                'action': 'mark_read'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
