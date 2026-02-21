# Like Functionality & Notification System Implementation Guide

## Overview

This document details the complete implementation of Like functionality with integrated automatic notifications. Users can like/unlike posts, and the system automatically creates notifications for post authors while respecting user preferences.

---

## Table of Contents

1. [Like System](#like-system)
2. [Notification System](#notification-system)
3. [Integration](#integration)
4. [API Endpoints](#api-endpoints)
5. [Examples](#examples)
6. [Testing](#testing)
7. [Database Schema](#database-schema)

---

## Like System

### Overview

The Like system allows users to like and unlike posts with the following features:
- Prevent duplicate likes (unique constraint on user + post)
- Unlike posts to remove likes
- Accurate like counts
- Thread-safe operations

### Like Model

**Location**: [posts/models.py](posts/models.py)

```python
class Like(models.Model):
    user = ForeignKey(CustomUser)          # User who liked
    post = ForeignKey(Post)                # Post being liked
    created_at = DateTimeField()           # When the like was created
    
    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes
```

### Key Features

| Feature | Details |
|---------|---------|
| **Uniqueness** | Users can only like a post once (enforced by database constraint) |
| **Timestamps** | Tracks when each like was created |
| **Cascade Delete** | Deleting user or post also deletes associated likes |
| **Ordering** | Likes ordered by most recent first |

### Like Views

**Location**: [posts/views.py](posts/views.py)

#### Like a Post

```python
@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
def like(self, request, id=None):
    """Like a post - prevents duplicate likes"""
    post = self.get_object()
    
    if post.likes.filter(user=request.user).exists():
        return Response({'error': 'Already liked'}, status=400)
    
    Like.objects.create(user=request.user, post=post)
    return Response({'likes_count': post.likes.count()}, status=201)
```

**Features:**
- ✅ Prevents duplicate likes
- ✅ Returns updated like count
- ✅ Returns 201 (Created) status
- ✅ Triggers notification signal

#### Unlike a Post

```python
@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
def unlike(self, request, id=None):
    """Unlike a post - removes the like"""
    post = self.get_object()
    
    like = post.likes.filter(user=request.user).first()
    if not like:
        return Response({'error': 'Not liked'}, status=400)
    
    like.delete()
    return Response({'likes_count': post.likes.count()}, status=200)
```

**Features:**
- ✅ Validates user has actually liked the post
- ✅ Returns updated like count
- ✅ Properly removes the Like object
- ✅ Triggers notification deletion (if implemented)

---

## Notification System

### Overview

The notification system automatically creates notifications when:
- A user is followed
- A post receives a like
- A post receives a comment
- A comment receives a reply

All notifications respect user preferences and can be retrieved, marked as read, and bulk-managed via REST API.

### Notification Models

**Location**: [notifications/models.py](notifications/models.py)

#### Notification Model

```python
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'New Follower'),
        ('like', 'Post Liked'),
        ('comment', 'Post Commented'),
        ('mention', 'User Mentioned'),
        ('reply', 'Comment Reply'),
    )
    
    recipient = ForeignKey(CustomUser)        # Who receives notification
    actor = ForeignKey(CustomUser)            # Who triggered it
    verb = CharField(choices=NOTIFICATION_TYPES)  # Type of action
    
    content_type = ForeignKey(ContentType)    # Generic reference
    object_id = PositiveIntegerField()        # Generic reference
    target = GenericForeignKey()              # The object (Post/Comment/etc)
    
    is_read = BooleanField(default=False)     # Read status
    created_at = DateTimeField()              # Creation time
    updated_at = DateTimeField()              # Last update time
    
    class Meta:
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
```

#### NotificationPreference Model

```python
class NotificationPreference(models.Model):
    user = OneToOneField(CustomUser)
    
    # In-app notifications
    follow_notifications = BooleanField(default=True)
    like_notifications = BooleanField(default=True)
    comment_notifications = BooleanField(default=True)
    mention_notifications = BooleanField(default=True)
    reply_notifications = BooleanField(default=True)
    
    # Email notifications
    email_on_follow = BooleanField(default=False)
    email_on_like = BooleanField(default=False)
    email_on_comment = BooleanField(default=False)
```

### Signal Handlers

**Location**: [notifications/signals.py](notifications/signals.py)

Signals automatically create notifications when events occur:

#### Like Signal Handler

```python
@receiver(post_save, sender=Like)
def like_created_signal(sender, instance, created, **kwargs):
    if created:
        # Skip notification if user likes their own post
        if instance.user != instance.post.author:
            
            # Check user preference
            preference = NotificationPreference.objects.get_or_create(
                user=instance.post.author
            )[0]
            if not preference.like_notifications:
                return
            
            # Create notification
            Notification.objects.create(
                recipient=instance.post.author,
                actor=instance.user,
                verb='like',
                content_type=ContentType.objects.get_for_model(Post),
                object_id=instance.post.id
            )
```

**Logic:**
1. Skip notifications for self-likes
2. Respect user preferences
3. Create generic notification with Post as target
4. Automatically run on Like creation

#### Comment Signal Handler

```python
@receiver(post_save, sender=Comment)
def comment_created_signal(sender, instance, created, **kwargs):
    if created:
        # Notify post author (if not their own comment)
        if instance.post.author != instance.author:
            # Check preference and create notification
            ...
        
        # Notify parent comment author on replies
        if instance.parent_comment:
            parent_author = instance.parent_comment.author
            if parent_author != instance.author:
                # Create reply notification with verb='reply'
                ...
```

**Logic:**
1. Notifies post author on comments
2. Notifies comment author on replies
3. Different verb types (comment vs reply)
4. Respects preferences at each level

### Notification Views

**Location**: [notifications/views.py](notifications/views.py)

#### NotificationViewSet

Provides REST API endpoints for:
- ✅ List notifications (with filtering, pagination)
- ✅ Retrieve single notification (with full details)
- ✅ Mark as read (single or bulk)
- ✅ Get unread count
- ✅ Delete operations
- ✅ Clear all notifications

#### NotificationPreferenceView

Provides REST API endpoints for:
- ✅ Get preferences (auto-creates if needed)
- ✅ Update preferences (partial updates supported)

---

## Integration

### How Like Triggers Notifications

```
User A likes Post by User B
          ↓
    Like.objects.create()
          ↓
    post_save signal fires
          ↓
    like_created_signal() runs
          ↓
    Check: Is User A ≠ User B? ✓
          ↓
    Check: User B has like_notifications enabled? ✓
          ↓
    Notification.objects.create(
        recipient=User B,
        actor=User A,
        verb='like',
        target=Post
    )
          ↓
    User B receives notification
```

### How Comments Trigger Notifications

```
User C comments on Post by User B
          ↓
    Comment.objects.create()
          ↓
    post_save signal fires
          ↓
    comment_created_signal() runs
          ↓
    Check: Is User C ≠ User B? ✓
          ↓
    Check: User B has comment_notifications enabled? ✓
          ↓
    Notification.objects.create(
        recipient=User B,
        actor=User C,
        verb='comment',
        target=Comment
    )
          ↓
    User B receives notification
```

### How Replies Trigger Notifications

```
User D replies to Comment by User C
          ↓
    Comment.objects.create(parent_comment=Comment C)
          ↓
    post_save signal fires
          ↓
    comment_created_signal() runs
          ↓
    Check: parent_comment exists? ✓
    Check: Is User D ≠ User C? ✓
          ↓
    Check: User C has reply_notifications enabled? ✓
          ↓
    Notification.objects.create(
        recipient=User C,
        actor=User D,
        verb='reply',
        target=Reply Comment
    )
          ↓
    User C receives reply notification
```

---

## API Endpoints

### Post Like Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/posts/{id}/like/` | POST | ✅ Required | Like a post |
| `/api/posts/{id}/unlike/` | POST | ✅ Required | Unlike a post |

### Notification Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/notifications/` | GET | ✅ Required | List notifications |
| `/api/notifications/{id}/` | GET | ✅ Required | Get notification details |
| `/api/notifications/{id}/mark_read/` | POST | ✅ Required | Mark single as read |
| `/api/notifications/mark_all_read/` | POST | ✅ Required | Mark all as read |
| `/api/notifications/unread_count/` | GET | ✅ Required | Get unread count |
| `/api/notifications/bulk_action/` | POST | ✅ Required | Bulk actions |
| `/api/notifications/clear_all/` | DELETE | ✅ Required | Delete all |
| `/api/preferences/` | GET | ✅ Required | Get preferences |
| `/api/preferences/` | PATCH | ✅ Required | Update preferences |

### Comment Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/posts/{id}/comment/` | POST | ✅ Required | Add comment or reply |
| `/api/posts/{id}/comments/` | GET | ✅ Required | List comments |

---

## Examples

### Like a Post

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/posts/1/like/
```

**Response (201 Created):**
```json
{
  "message": "Post liked successfully",
  "likes_count": 5
}
```

### Unlike a Post

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/posts/1/unlike/
```

**Response (200 OK):**
```json
{
  "message": "Post unliked successfully",
  "likes_count": 4
}
```

### Get Notifications

**Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/notifications/?unread=true
```

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "recipient": 1,
      "actor": {
        "id": 2,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "verb": "like",
      "is_read": false,
      "created_at": "2026-02-21T10:30:00Z"
    }
  ]
}
```

### Mark Notification as Read

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/notifications/1/mark_read/
```

**Response (200 OK):**
```json
{
  "message": "Notification marked as read",
  "notification": { ... }
}
```

### Comment on a Post

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great post!"}' \
  http://localhost:8000/api/posts/1/comment/
```

**Response (201 Created):**
```json
{
  "id": 1,
  "author": {
    "id": 2,
    "username": "john_doe",
    ...
  },
  "content": "Great post!",
  "parent_comment": null,
  "replies": [],
  "is_reply": false,
  "reply_count": 0,
  "created_at": "2026-02-21T10:30:00Z"
}
```

### Reply to a Comment

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d {
    "content": "I agree!",
    "parent_comment": 1
  }' \
  http://localhost:8000/api/posts/1/comment/
```

**Response (201 Created):**
```json
{
  "id": 2,
  "author": { ... },
  "content": "I agree!",
  "parent_comment": 1,
  "replies": [],
  "is_reply": true,
  "reply_count": 0,
  "created_at": "2026-02-21T10:31:00Z"
}
```

### Update Preferences

**Request:**
```bash
curl -X PATCH \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "like_notifications": false,
    "email_on_comment": true
  }' \
  http://localhost:8000/api/preferences/
```

**Response (200 OK):**
```json
{
  "message": "Notification preferences updated successfully",
  "preferences": {
    "id": 1,
    "user": 1,
    "follow_notifications": true,
    "like_notifications": false,
    "comment_notifications": true,
    "mention_notifications": true,
    "reply_notifications": true,
    "email_on_follow": false,
    "email_on_like": false,
    "email_on_comment": true
  }
}
```

### Get Unread Count

**Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/notifications/unread_count/
```

**Response (200 OK):**
```json
{
  "unread_count": 3
}
```

### Bulk Mark Notifications as Read

**Request:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_ids": [1, 2, 3],
    "action": "mark_read"
  }' \
  http://localhost:8000/api/notifications/bulk_action/
```

**Response (200 OK):**
```json
{
  "message": "Marked 3 notification(s) as read",
  "count": 3
}
```

---

## Testing

### Run All Tests

```bash
# Run test file
python manage.py test test_like_and_notifications

# With verbose output
python manage.py test test_like_and_notifications -v 2

# Run specific test class
python manage.py test test_like_and_notifications.LikeFunctionalityTests

# Run specific test method
python manage.py test test_like_and_notifications.LikeFunctionalityTests.test_like_post_creates_like_object
```

### Test Coverage

The test suite includes:

✅ **Like Functionality Tests** (7 tests)
- Like post creates Like object
- Cannot like post twice
- Unlike removes like
- Cannot unlike post not liked
- Like count accuracy
- Multiple users can like same post
- Self-likes skip notification

✅ **Like-Notification Integration Tests** (2 tests)
- Like creates notification for post author
- Notification respects user preference (disabled)
- Notification respects user preference (enabled)

✅ **Comment-Notification Integration Tests** (3 tests)
- Comment creates notification for post author
- Reply to comment creates notification for commenter
- Nested comments structure

✅ **Notification Preference Tests** (2 tests)
- Get preferences creates default
- Update preferences

✅ **Notification Retrieval Tests** (7 tests)
- List notifications
- Filter unread notifications
- Get unread count
- Mark notification read
- Mark all read
- Bulk action mark read

### Manual Testing

Use the curl examples provided in [Examples](#examples) section to test endpoints manually.

---

## Database Schema

### Like Table

```sql
CREATE TABLE posts_like (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id),
    post_id BIGINT NOT NULL REFERENCES posts_post(id),
    created_at DATETIME NOT NULL,
    UNIQUE(user_id, post_id),
    INDEX(created_at DESC),
    INDEX(post_id, created_at DESC)
);
```

### Comment Table (Updated)

```sql
CREATE TABLE posts_comment (
    id BIGINT PRIMARY KEY,
    author_id BIGINT NOT NULL REFERENCES accounts_customuser(id),
    post_id BIGINT NOT NULL REFERENCES posts_post(id),
    parent_comment_id BIGINT REFERENCES posts_comment(id),
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX(post_id, created_at DESC),
    INDEX(parent_comment_id, created_at DESC)
);
```

### Notification Table

```sql
CREATE TABLE notifications_notification (
    id BIGINT PRIMARY KEY,
    recipient_id BIGINT NOT NULL REFERENCES accounts_customuser(id),
    actor_id BIGINT NOT NULL REFERENCES accounts_customuser(id),
    verb VARCHAR(10) NOT NULL,
    content_type_id INT REFERENCES django_content_type(id),
    object_id INT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX(recipient_id, created_at DESC),
    INDEX(recipient_id, is_read)
);
```

### NotificationPreference Table

```sql
CREATE TABLE notifications_notificationpreference (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES accounts_customuser(id),
    follow_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    like_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    comment_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    mention_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    reply_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    email_on_follow BOOLEAN NOT NULL DEFAULT FALSE,
    email_on_like BOOLEAN NOT NULL DEFAULT FALSE,
    email_on_comment BOOLEAN NOT NULL DEFAULT FALSE
);
```

---

## Common Issues & Troubleshooting

### Issue: Notifications not creating on like

**Cause:** Signals not imported or app not in INSTALLED_APPS

**Solution:**
1. Verify `notifications` in settings.INSTALLED_APPS
2. Verify signals imported in notifications/apps.py ready() method
3. Restart Django development server

### Issue: Duplicate likes allowed

**Cause:** Unique constraint not enforced

**Solution:**
1. Run migrations: `python manage.py migrate`
2. Verify constraint in database

### Issue: Like count not updating

**Cause:** ORM cache or query issues

**Solution:**
1. Refresh object: `post.refresh_from_db()`
2. Use fresh query: `post.likes.count()`

### Issue: Nested replies not showing

**Cause:** Only top-level comments fetched

**Solution:**
The `/api/posts/{id}/comments/` endpoint returns top-level comments with nested replies in the `replies` field. This is by design for performance.

---

## Performance Optimization Tips

1. **Use Pagination:** Fetch notifications in pages (default 20 per page)
2. **Filter Unread:** Use `?unread=true` to get only unread
3. **Bulk Operations:** Prefer bulk_action over individual updates
4. **Prefetch Related:** ViewSet already optimizes queries
5. **Index Usage:** Queries use (recipient, -created_at) and (recipient, is_read) indexes

---

## Future Enhancements

- [ ] Email notifications
- [ ] Push notifications
- [ ] Notification digest (daily/weekly summary)
- [ ] Notification groups (combine similar notifications)
- [ ] Read receipts
- [ ] Notification expiry (auto-delete old ones)
- [ ] Real-time WebSocket notifications

---

**Last Updated**: February 21, 2026
**Version**: 1.0
**Status**: Production Ready
