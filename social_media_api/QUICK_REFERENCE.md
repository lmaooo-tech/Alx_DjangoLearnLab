# Quick Reference: Like Functionality & Notification System

**Created**: February 21, 2026  
**Status**: Production Ready

---

## 1-Minute Overview

The Like and Notification system works like this:

```
User A likes Post by User B
           ↓
Signal fires automatically
           ↓
Checks: User A ≠ User B? + Preference enabled?
           ↓
Notification created for User B
           ↓
User B sees notification via API
```

---

## Most Common Operations

### Like a Post
```bash
POST /api/posts/1/like/
Authorization: Token YOUR_TOKEN
```

### Unlike a Post
```bash
POST /api/posts/1/unlike/
Authorization: Token YOUR_TOKEN
```

### Get My Notifications
```bash
GET /api/notifications/
Authorization: Token YOUR_TOKEN
```

### Get Unread Count
```bash
GET /api/notifications/unread_count/
Authorization: Token YOUR_TOKEN
```

### Mark All as Read
```bash
POST /api/notifications/mark_all_read/
Authorization: Token YOUR_TOKEN
```

### Update My Preferences
```bash
PATCH /api/preferences/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "like_notifications": false,
  "comment_notifications": true,
  "email_on_like": true
}
```

### Comment on Post
```bash
POST /api/posts/1/comment/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "content": "Great post!"
}
```

### Reply to Comment
```bash
POST /api/posts/1/comment/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "content": "I agree!",
  "parent_comment": 5
}
```

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| posts/models.py | Like model + Comment with parent | 150+ |
| posts/views.py | Like/unlike + comment actions | 374 |
| posts/serializers.py | Comment with nested replies | 180+ |
| notifications/models.py | Notification + Preference | 160+ |
| notifications/views.py | Notification API | 250+ |
| notifications/signals.py | Auto-notification creation | 140 |
| notifications/serializers.py | Notification serializers | 180+ |

---

## API Endpoints

**Likes**: 2 endpoints
```
POST /api/posts/{id}/like/
POST /api/posts/{id}/unlike/
```

**Comments**: 2 endpoints
```
POST /api/posts/{id}/comment/      (or reply with parent_comment)
GET  /api/posts/{id}/comments/
```

**Notifications**: 8 endpoints
```
GET    /api/notifications/
GET    /api/notifications/{id}/
POST   /api/notifications/{id}/mark_read/
POST   /api/notifications/mark_all_read/
GET    /api/notifications/unread_count/
POST   /api/notifications/bulk_action/
DELETE /api/notifications/clear_all/
GET    /api/preferences/
PATCH  /api/preferences/
```

---

## How Signals Work

### On Like Created
```python
# Automatically triggers this signal:
@receiver(post_save, sender=Like)
def like_created_signal(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.post.author:  # Not self-like
            preference = NotificationPreference.objects.get_or_create(user=instance.post.author)[0]
            if preference.like_notifications:      # Preference enabled
                Notification.objects.create(
                    recipient=instance.post.author,
                    actor=instance.user,
                    verb='like'
                )
```

### On Comment Created
```python
# Automatically triggers this signal:
@receiver(post_save, sender=Comment)
def comment_created_signal(sender, instance, created, **kwargs):
    if created:
        # Notify post author
        if instance.post.author != instance.author:
            # Create comment notification
        
        # Notify parent commenter (if reply)
        if instance.parent_comment:
            # Create reply notification
```

---

## Testing

```bash
# Run all tests
python manage.py test test_like_and_notifications -v 2

# Total: 21 tests
# Like tests: 7
# Notification tests: 7
# Comment tests: 3
# Preference tests: 2
# Retrieval tests: 2
```

---

## Database Schema (Simplified)

```sql
-- Like
id | user_id | post_id | created_at | UNIQUE(user_id, post_id)

-- Comment (Updated)
id | author_id | post_id | parent_comment_id | content | created_at

-- Notification
id | recipient_id | actor_id | verb | content_type_id | object_id | is_read | created_at

-- NotificationPreference
id | user_id | follow_notifications | like_notifications | comment_notifications | ...
```

---

## Response Examples

### Like Response
```json
{
  "message": "Post liked successfully",
  "likes_count": 5
}
```

### Notification List
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "recipient": 1,
      "actor": { "id": 2, "username": "john_doe" },
      "verb": "like",
      "is_read": false,
      "created_at": "2026-02-21T10:30:00Z"
    }
  ]
}
```

### Comment Response
```json
{
  "id": 1,
  "author": { "id": 2, "username": "john_doe" },
  "content": "Great post!",
  "parent_comment": null,
  "replies": [],
  "reply_count": 0,
  "is_reply": false,
  "created_at": "2026-02-21T10:30:00Z"
}
```

### Preference Response
```json
{
  "id": 1,
  "user": 1,
  "follow_notifications": true,
  "like_notifications": true,
  "comment_notifications": true,
  "mention_notifications": true,
  "reply_notifications": true,
  "email_on_follow": false,
  "email_on_like": false,
  "email_on_comment": false
}
```

---

## Error Responses

```json
// Already liked
{
  "error": "You have already liked this post."
}

// Not liked
{
  "error": "You have not liked this post."
}

// Invalid parent comment
{
  "error": "Parent comment not found or does not belong to this post."
}

// Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Configuration

### settings.py
```python
INSTALLED_APPS = [
    ...
    'accounts',
    'posts',
    'notifications',  # Don't forget to add!
]
```

### urls.py
```python
urlpatterns = [
    path('api/auth/', include('accounts.urls')),
    path('api/', include('posts.urls')),
    path('api/', include('notifications.urls')),  # Add this!
]
```

---

## Permissions

All Like and Notification endpoints require:
- ✅ Authentication (Token required)
- ✅ User must be authenticated
- ✅ Can only access own notifications/preferences

---

## Performance Tips

1. **Get unread count** - Use `/api/notifications/unread_count/` instead of listing all
2. **Filter notifications** - Use `?unread=true` to get only unread
3. **Bulk operations** - Use bulk_action endpoint for multiple changes
4. **Pagination** - Default 20 items per page, extend if needed

---

## Common Mistakes

❌ **Wrong**: Not checking if user is authenticated
```python
# This will fail if user not authenticated
if post.likes.filter(user=request.user).exists():
```

✅ **Right**: Use permission_classes
```python
@permission_classes([IsAuthenticated])
def like(self, request):
    ...
```

---

❌ **Wrong**: Manually creating notifications
```python
# Users might not want these notifications
Notification.objects.create(...)
```

✅ **Right**: Use signal handlers
```python
# Respects user preferences automatically
@receiver(post_save, sender=Like)
def like_created_signal(...):
    # Checks preference internally
    ...
```

---

## Debugging

```bash
# Check if app installed
python manage.py shell
>>> from django.apps import apps
>>> apps.get_app_config('notifications')

# Check if signals registered
python manage.py shell
>>> from django.db.models import signals
>>> from posts.models import Like
>>> signals.post_save.has_listeners(Like)  # Should be True

# Check database
python manage.py shell
>>> from notifications.models import Notification
>>> Notification.objects.all()

# Check preferences
python manage.py shell
>>> from notifications.models import NotificationPreference
>>> NotificationPreference.objects.all()
```

---

## Migrations

```bash
# Create migrations for notifications
python manage.py makemigrations notifications

# Create migrations for posts (parent_comment)
python manage.py makemigrations posts

# Apply all migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

---

## Production Checklist

- [ ] Run all tests: `python manage.py test`
- [ ] Check migrations: `python manage.py migrate --check`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set SECRET_KEY via environment variable
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure logging
- [ ] Set up error monitoring
- [ ] Test email notifications (when implemented)

---

## Need More Info?

- **API Details**: See `NOTIFICATION_SYSTEM_DOCUMENTATION.md`
- **Integration Guide**: See `LIKE_AND_NOTIFICATION_SYSTEM.md`
- **Full Project**: See `PROJECT_STATUS_TRACKER.md`
- **Tests**: See `test_like_and_notifications.py`
- **Code Examples**: See implementation files

---

**Status**: ✅ Production Ready  
**Last Updated**: February 21, 2026  
**Testing**: 21 comprehensive tests included
