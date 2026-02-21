# Notification System Documentation

## Overview

The notification system enables users to receive real-time updates about important activities on the social media platform, including new followers, post likes, and comments. The system respects user preferences and provides granular control over notification types and delivery methods.

## Table of Contents

1. [Architecture](#architecture)
2. [Models](#models)
3. [API Endpoints](#api-endpoints)
4. [Signal Handlers](#signal-handlers)
5. [User Preferences](#user-preferences)
6. [Examples](#examples)
7. [Testing](#testing)

## Architecture

### Core Components

1. **Notification Model**: Stores notification data with generic foreign key relationships
2. **NotificationPreference Model**: Stores user preferences for notification types
3. **Signal Handlers**: Automatically create notifications when events occur
4. **ViewSet**: Provides REST API endpoints for notification management
5. **Serializers**: Handle data serialization and validation

### Event Types

The system supports five notification event types:

| Type | Verb | Description |
|------|------|-------------|
| New Follower | `follow` | When a user follows another user |
| Post Liked | `like` | When a post receives a like |
| Post Commented | `comment` | When a post receives a comment |
| User Mentioned | `mention` | When a user is mentioned in a comment |
| Comment Reply | `reply` | When a comment receives a reply |

### Technology Stack

- **Django 6.0.1**: Core framework
- **Django REST Framework**: API development
- **Django Signals**: Event-driven notifications
- **GenericForeignKey**: Polymorphic relationships
- **ContentType**: Flexible object references

## Models

### Notification Model

```python
class Notification(models.Model):
    recipient = ForeignKey(CustomUser)  # User receiving the notification
    actor = ForeignKey(CustomUser)      # User triggering the notification
    verb = CharField()                   # Type of notification
    content_type = ForeignKey(ContentType)  # Generic reference
    object_id = PositiveIntegerField()      # Generic reference
    target = GenericForeignKey()        # The object being notified about
    is_read = BooleanField()            # Read status
    created_at = DateTimeField()        # Creation timestamp
    updated_at = DateTimeField()        # Last update timestamp
```

#### Key Features

- **Generic Foreign Key**: Allows notifications to reference any model (Post, Comment, Follow)
- **Indexed Queries**: Optimized with indexes on (recipient, -created_at) and (recipient, is_read) for fast queries
- **Timestamps**: Automatic tracking of creation and update times
- **Read Status**: Track which notifications the user has viewed

### NotificationPreference Model

```python
class NotificationPreference(models.Model):
    user = OneToOneField(CustomUser)    # User owning preferences
    
    # Notification toggles
    follow_notifications = BooleanField(default=True)
    like_notifications = BooleanField(default=True)
    comment_notifications = BooleanField(default=True)
    mention_notifications = BooleanField(default=True)
    reply_notifications = BooleanField(default=True)
    
    # Email notification toggles
    email_on_follow = BooleanField(default=False)
    email_on_like = BooleanField(default=False)
    email_on_comment = BooleanField(default=False)
```

#### Key Features

- **User Control**: Users can enable/disable each notification type individually
- **Email Delivery**: Optional email notifications for important events
- **Default Enabled**: All in-app notifications enabled by default
- **OneToOne Relationship**: One preference settings per user

## API Endpoints

### Notification Endpoints

#### List Notifications

```
GET /api/notifications/
```

Returns paginated list of notifications for the authenticated user.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)
- `unread`: Filter by read status (`true` or `false`)
- `verb`: Filter by notification type (follow, like, comment, mention, reply)

**Response:**
```json
{
  "count": 105,
  "next": "http://api.example.com/api/notifications/?page=2",
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
      "created_at": "2026-02-21T10:30:00Z",
      "updated_at": "2026-02-21T10:30:00Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Notifications retrieved successfully
- `401 Unauthorized`: User not authenticated
- `403 Forbidden`: Access denied

#### Get Single Notification

```
GET /api/notifications/{id}/
```

Returns detailed information about a specific notification, including the referenced object.

**Response:**
```json
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
  "target_type": "post",
  "target_id": 5,
  "target_data": {
    "id": 5,
    "title": "My First Post",
    "content": "This is interesting...",
    "author": 1,
    "created_at": "2026-02-21T09:00:00Z"
  },
  "created_at": "2026-02-21T10:30:00Z",
  "updated_at": "2026-02-21T10:30:00Z"
}
```

#### Mark Notification as Read

```
POST /api/notifications/{id}/mark_read/
```

Marks a specific notification as read.

**Response:**
```json
{
  "message": "Notification marked as read",
  "notification": { ... }
}
```

#### Mark All Notifications as Read

```
POST /api/notifications/mark_all_read/
```

Marks all unread notifications for the user as read.

**Response:**
```json
{
  "message": "Marked 5 notification(s) as read",
  "count": 5
}
```

#### Get Unread Count

```
GET /api/notifications/unread_count/
```

Returns the count of unread notifications for the user.

**Response:**
```json
{
  "unread_count": 5
}
```

#### Bulk Notification Actions

```
POST /api/notifications/bulk_action/
```

Perform bulk actions on multiple notifications.

**Request Body:**
```json
{
  "notification_ids": [1, 2, 3, 4, 5],
  "action": "mark_read"
}
```

**Available Actions:**
- `mark_read`: Mark notifications as read
- `mark_unread`: Mark notifications as unread
- `delete`: Delete notifications permanently

**Response:**
```json
{
  "message": "Marked 5 notification(s) as read",
  "count": 5
}
```

#### Clear All Notifications

```
DELETE /api/notifications/clear_all/
```

Delete all notifications for the current user.

**Response:**
```json
{
  "message": "Deleted all 23 notification(s)",
  "count": 23
}
```

### Notification Preferences Endpoints

#### Get User Preferences

```
GET /api/preferences/
```

Retrieve notification preferences for the authenticated user. Creates default preferences if they don't exist.

**Response:**
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

#### Update User Preferences

```
PATCH /api/preferences/
```

Update notification preferences. Supports partial updates.

**Request Body:**
```json
{
  "follow_notifications": false,
  "email_on_like": true,
  "comment_notifications": false
}
```

**Response:**
```json
{
  "message": "Notification preferences updated successfully",
  "preferences": {
    "id": 1,
    "user": 1,
    "follow_notifications": false,
    "like_notifications": true,
    "comment_notifications": false,
    "mention_notifications": true,
    "reply_notifications": true,
    "email_on_follow": false,
    "email_on_like": true,
    "email_on_comment": false
  }
}
```

## Signal Handlers

### Overview

Signal handlers automatically create notifications when events occur in the system. They run synchronously when the triggering action completes.

### Follow Signal Handler

**Trigger:** When a user is followed via the followers relationship

**Code:**
```python
def create_follow_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for follower_id in pk_set:
            # Check user preferences
            # Create notification with verb='follow'
```

**Flow:**
1. User A follows User B
2. Signal triggers with User B as instance, User A in pk_set
3. Checks if User B has follow notifications enabled
4. Creates follow Notification with:
   - recipient = User B
   - actor = User A
   - verb = 'follow'

### Like Signal Handler

**Trigger:** When a Like object is created

**Code:**
```python
@receiver(post_save, sender=Like)
def like_created_signal(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.author:
        # Check preferences
        # Create notification with verb='like'
```

**Flow:**
1. User A likes Post created by User B
2. Like object is saved to database
3. Signal triggers
4. Checks if Post author is different from Like actor (skip self-likes)
5. Checks if User B has like notifications enabled
6. Creates Like Notification with:
   - recipient = User B (post author)
   - actor = User A (liker)
   - verb = 'like'
   - target = Post B

### Comment Signal Handler

**Trigger:** When a Comment object is created

**Code:**
```python
@receiver(post_save, sender=Comment)
def comment_created_signal(sender, instance, created, **kwargs):
    if created:
        # Notify post author
        # Notify parent comment author (for replies)
```

**Flow:**

**For Post Comments:**
1. User A comments on Post by User B
2. Comment object is saved
3. Signal triggers
4. Checks if commenter is different from post author
5. Checks if User B has comment notifications enabled
6. Creates Comment Notification with:
   - recipient = User B
   - actor = User A
   - verb = 'comment'
   - target = Comment

**For Comment Replies:**
1. User A replies to Comment by User B
2. Comment has parent_comment set
3. Signal triggers with parent_comment present
4. Checks if replier is different from parent comment author
5. Checks if User B has reply notifications enabled
6. Creates Reply Notification with:
   - recipient = User B
   - actor = User A
   - verb = 'reply'
   - target = Reply Comment

### Signal Registration

All signals are automatically registered when the notifications app initializes via the `ready()` method in [apps.py](notifications/apps.py):

```python
def ready(self):
    import notifications.signals  # noqa
```

## User Preferences

### Creating Preferences

Preferences are automatically created with default settings when:
1. A user first receives a notification
2. User explicitly accesses the preferences endpoint

### Preference Types

#### In-App Notifications
- **follow_notifications**: Receive notifications when followed (default: True)
- **like_notifications**: Receive notifications when liking posts (default: True)
- **comment_notifications**: Receive notifications on post comments (default: True)
- **mention_notifications**: Receive notifications when mentioned (default: True)
- **reply_notifications**: Receive notifications on comment replies (default: True)

#### Email Notifications
- **email_on_follow**: Receive emails for new followers (default: False)
- **email_on_like**: Receive emails for post likes (default: False)
- **email_on_comment**: Receive emails for post comments (default: False)

### Managing Preferences

Users can manage their preferences via the API:

```bash
# Get current preferences
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/preferences/

# Disable all notifications except comments
curl -X PATCH -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "follow_notifications": false,
    "like_notifications": false,
    "mention_notifications": false,
    "reply_notifications": false
  }' \
  http://localhost:8000/api/preferences/
```

## Examples

### Example 1: Follow Notification Flow

```
Scenario: User B follows User A

1. Request:
   POST /api/follow/
   {
     "user_id": 1  // User A
   }

2. Follow created → Signal triggers
   create_follow_notification(actor=User B, target=User A)

3. NotificationPreference check:
   User A.preference.follow_notifications == True ✓

4. Notification Created:
   {
     "recipient": User A,
     "actor": User B,
     "verb": "follow",
     "is_read": false,
     "created_at": "2026-02-21T10:30:00Z"
   }

5. User A fetches notifications:
   GET /api/notifications/
   → Sees "john_doe started following you" notification
```

### Example 2: Like Notification with Preference Check

```
Scenario: Like notification when preference is disabled

1. User A likes post by User B
   POST /api/posts/{post_id}/like/

2. Like.post_save signal triggers
   like_created_signal(actor=User A, post=User B's post)

3. NotificationPreference check:
   User B.preference.like_notifications == False ✗

4. Notification NOT created
   Signal returns early, skipping creation

5. User B receives NO notification
```

### Example 3: Bulk Actions

```
Scenario: Mark multiple notifications as read

1. Request:
   POST /api/notifications/bulk_action/
   {
     "notification_ids": [1, 2, 3, 4, 5],
     "action": "mark_read"
   }

2. Response:
   {
     "message": "Marked 5 notification(s) as read",
     "count": 5
   }

3. Subsequent GET /api/notifications/?unread=true
   → Returns 0 results (all marked as read)
```

### Example 4: Replying to Comments

```
Scenario: Reply notification chain

1. User A comments on post
   POST /api/posts/{post_id}/comments/
   → Creates Comment A

2. User B replies to User A's comment
   POST /api/posts/{post_id}/comments/
   {
     "content": "Great point!",
     "parent_comment": 1  // Comment A
   }

3. Comment.post_save signal triggers
   comment_created_signal(instance=Comment B, parent_comment=Comment A)

4. Two notifications created:
   a) Post author notification (if different from User B)
   b) Parent comment author (User A) notification
      - verb = "reply"
      - This is a mention-intent notification

5. User A receives:
   "john_doe replied to your comment"
```

## Testing

### Running Notification Tests

```bash
# Run all notification tests
python manage.py test notifications

# Run specific test class
python manage.py test notifications.tests.NotificationSignalTests

# Run with verbose output
python manage.py test notifications -v 2
```

### Manual Testing with cURL

#### Create a follow relationship
```bash
curl -X POST \
  -H "Authorization: Token USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}' \
  http://localhost:8000/api/auth/follow/
```

#### Check notifications
```bash
curl -H "Authorization: Token USER_A_TOKEN" \
  http://localhost:8000/api/notifications/
```

#### Mark as read
```bash
curl -X POST \
  -H "Authorization: Token USER_A_TOKEN" \
  http://localhost:8000/api/notifications/1/mark_read/
```

### Test Scenarios

1. **Follow Signal Test**
   - Create user and follow another
   - Verify notification created
   - Verify correct fields populated

2. **Like Signal Test**
   - Create post, like it
   - Verify notification created for author
   - Verify self-likes skip notification

3. **Comment Signal Test**
   - Create comment on post
   - Verify notification for post author
   - Verify notification excludes self-comments

4. **Reply Notification Test**
   - Create nested comments
   - Verify reply notification created
   - Verify correct recipient for nested replies

5. **Preference Enforcement**
   - Disable like notifications
   - Create like
   - Verify no notification created

6. **Bulk Operations**
   - Create multiple notifications
   - Test bulk mark_read
   - Test bulk delete
   - Verify count accuracy

## Integration with Existing Features

### With Follow System

The notification system integrates with the follow system created in Step 2:
- Uses `CustomUser.followers` ManyToMany relationship
- Signals detect when users are added to followers
- Creates notifications respecting preferences

### With Like System

The notification system integrates with the Like model from Step 3:
- Listens to Like model creation
- Extracts post author and post information
- Creates notifications with post as target

### With Comment System

The notification system integrates with the Comment model from Step 4:
- Listens to Comment model creation
- Handles nested comments and replies
- Creates appropriate notifications with comment as target

## Performance Considerations

### Optimization Strategies

1. **Database Indexes**
   - Index on (recipient, -created_at) for list queries
   - Index on (recipient, is_read) for unread count queries
   - Dramatically improves query performance for large notification sets

2. **Query Optimization**
   - Uses `select_related('actor', 'content_type')` in ViewSet
   - Reduces N+1 queries significantly
   - Lazy loads target objects only when needed

3. **Pagination**
   - Default 20 items per page
   - Reduces payload size
   - Improves API response times

### Recommended Pagination Strategy

For production systems with heavy notification volume:
```python
# Consider time-series pagination
# Fetch by timestamp rather than page number for better UX
GET /api/notifications/?since=2026-02-21T10:00:00Z&limit=20
```

## Future Enhancements

1. **Email Notifications**: Implement email sending for important events
2. **Push Notifications**: Add mobile push notification support
3. **Digest Notifications**: Combine multiple notifications into summaries
4. **Notification Channels**: Support for webhooks, SMS, etc.
5. **Read Receipts**: Track when notifications are opened
6. **Smart Notifications**: Use ML to prioritize important alerts
7. **Notification Groups**: Group related notifications together
8. **Notification Expiry**: Auto-delete old notifications

## Troubleshooting

### Notifications Not Creating

**Issue**: Notifications don't appear after following, liking, or commenting

**Solutions**:
1. Verify `notifications` app is in `INSTALLED_APPS`
2. Verify signals are imported in `apps.py`
3. Check user preference settings not disabling notifications
4. Verify recipient and actor are different (non-self actions)
5. Run migrations: `python manage.py migrate notifications`

### Preference Changes Not Applied

**Issue**: Disabling notification type doesn't stop notifications

**Solutions**:
1. Restart Django development server
2. Verify PATCH request properly formatted
3. Check response status is 200 OK
4. Verify user permissions for preference updates

### Database Errors on Migration

**Issue**: Error running `migrate`

**Solutions**:
1. Verify all models correctly defined
2. Clear migration history if needed: `rm notifications/migrations/0*.py`
3. Run makemigrations: `python manage.py makemigrations notifications`
4. Run migrations: `python manage.py migrate`

## Admin Interface

Access the Django admin to manage notifications:

```
URL: http://localhost:8000/admin/
Navigation: Notifications > Notifications
```

### Admin Features

- **List View**: See all notifications with recipient, actor, type, and date
- **Filter**: Filter by notification type, read status, and date range
- **Search**: Search by user email or username
- **Read-Only**: Notification data cannot be edited via admin
- **Preferences Management**: View/edit user notification preferences

### Admin Access Requirements

Admin account required:
```bash
python manage.py createsuperuser
```

---

**Last Updated**: February 21, 2026
**Version**: 1.0
**Status**: Production Ready
