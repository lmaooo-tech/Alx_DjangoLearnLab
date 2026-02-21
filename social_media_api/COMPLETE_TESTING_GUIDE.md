# Complete Testing Guide: Like & Notification System

**Date**: February 21, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready

---

## Overview

This guide provides comprehensive instructions for testing the Like and Notification system through three testing methods:
1. **Automated Testing** (Unit & Integration Tests)
2. **Manual Testing** (cURL commands)
3. **API Testing Tools** (Postman)

---

## Part 1: Automated Testing

### Prerequisites

```bash
# Ensure Django is installed
pip install django djangorestframework

# Verify project structure
python manage.py check
```

### Running Test Suite

#### Option 1: Run All Tests

```bash
# Run all 21 tests with verbose output
python manage.py test test_like_and_notifications -v 2

# Expected Output:
# test_like_and_notifications.LikeFunctionalityTests.test_like_post_creates_like_object ... ok
# test_like_and_notifications.LikeFunctionalityTests.test_cannot_like_post_twice ... ok
# ... (21 tests total)
# Ran 21 tests in 2.345s
# OK

# Exit code: 0 (success)
```

#### Option 2: Run Specific Test Class

```bash
# Test Like Functionality (7 tests)
python manage.py test test_like_and_notifications.LikeFunctionalityTests -v 2

# Test Like-Notification Integration (2 tests)
python manage.py test test_like_and_notifications.LikeNotificationIntegrationTests -v 2

# Test Comment-Notification Integration (3 tests)
python manage.py test test_like_and_notifications.CommentNotificationIntegrationTests -v 2

# Test Notification Retrieval (7 tests)
python manage.py test test_like_and_notifications.NotificationRetrievalTests -v 2

# Test Preferences (2 tests)
python manage.py test test_like_and_notifications.NotificationPreferenceTests -v 2
```

#### Option 3: Run Specific Test Method

```bash
# Test duplicate like prevention
python manage.py test test_like_and_notifications.LikeFunctionalityTests.test_cannot_like_post_twice -v 2

# Test like notification integration
python manage.py test test_like_and_notifications.LikeNotificationIntegrationTests.test_like_creates_notification_for_post_author -v 2
```

#### Option 4: Run with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test test_like_and_notifications

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Test Scenarios Covered

#### Like Functionality Tests

1. **test_like_post_creates_like_object**
   - Action: User likes a post
   - Expected: Like object created
   - Verifies: DB persistence, like count

2. **test_cannot_like_post_twice**
   - Action: User tries to like same post twice
   - Expected: 400 Bad Request on second attempt
   - Verifies: Unique constraint enforcement

3. **test_unlike_post_removes_like**
   - Action: User unlikes a post
   - Expected: Like object deleted
   - Verifies: DB deletion, like count updated

4. **test_cannot_unlike_post_not_liked**
   - Action: User tries to unlike post they didn't like
   - Expected: 400 Bad Request
   - Verifies: Validation logic

5. **test_like_count_is_accurate**
   - Action: Like then unlike post
   - Expected: Like count increments then decrements
   - Verifies: Accurate counting

6. **test_multiple_users_can_like_same_post**
   - Action: Multiple users like same post
   - Expected: All likes created successfully
   - Verifies: Multiple relationships

7. **test_cannot_like_own_post_notification_skip**
   - Action: User likes their own post
   - Expected: Like created but no notification
   - Verifies: Self-like notification prevention

#### Notification Integration Tests

8. **test_like_creates_notification_for_post_author**
   - Action: User A likes User B's post
   - Expected: Notification created for User B
   - Verifies: Signal triggers correctly

9. **test_notification_respects_user_preference_disabled**
   - Action: Disable like notifications, then like post
   - Expected: No notification created
   - Verifies: Preference enforcement

10. **test_comment_creates_notification_for_post_author**
    - Action: User comments on post
    - Expected: Notification for post author
    - Verifies: Comment signal handler

11. **test_reply_to_comment_creates_notification**
    - Action: User replies to comment
    - Expected: Notification for original commenter
    - Verifies: Reply signal handler

#### Notification Retrieval Tests

12. **test_list_notifications**
    - Action: Get user's notifications
    - Expected: 200 OK with paginated list
    - Verifies: Pagination, filtering

13. **test_filter_unread_notifications**
    - Action: Filter by unread status
    - Expected: Only unread notifications returned
    - Verifies: Query filtering

14. **test_get_unread_count**
    - Action: Get unread notification count
    - Expected: Correct count returned
    - Verifies: Count accuracy

15-21. **Additional Retrieval & Management Tests**
    - Mark as read (single & bulk)
    - Bulk operations
    - Preference management

### Interpreting Test Results

**Success Indicators:**
```bash
✓ All 21 tests pass (Ran 21 tests in X.XXXs OK)
✓ Command exits with status code 0
✓ No error messages in output
```

**Failure Indicators:**
```bash
✗ Test fails (FAIL: test_name)
✗ Non-zero exit code
✗ Error in signal handlers or database
✗ Missing migrations
```

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| ImportError | Missing app | Add to INSTALLED_APPS |
| No such table | Migration not run | `python manage.py migrate` |
| Signal not firing | Not imported | Import in apps.py ready() |
| Unique constraint error | Test data collision | Use unique test data |
| Authentication failed | No token provided | Add auth header |

---

## Part 2: Manual Testing with cURL

### Setup

```bash
# Start Django development server
python manage.py runserver

# In another terminal, export base URL
export BASE_URL="http://localhost:8000"
export API_URL="$BASE_URL/api"
```

### Test Scenario 1: Complete Like Flow

#### Step 1: Create Test Users

```bash
# Create User A
curl -X POST $API_URL/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userA",
    "email": "userA@test.com",
    "password": "testpass123"
  }'

# Response (201 Created):
# {
#   "user": {"id": 1, "username": "userA"},
#   "token": "token_userA"
# }

export TOKEN_A="token_userA"

# Create User B
curl -X POST $API_URL/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userB",
    "email": "userB@test.com",
    "password": "testpass123"
  }'

# Response (201 Created):
# {
#   "token": "token_userB"
# }

export TOKEN_B="token_userB"
```

#### Step 2: Create a Post

```bash
# User A creates a post
curl -X POST $API_URL/posts/ \
  -H "Authorization: Token $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"content": "My first post!"}'

# Response (201 Created):
# {
#   "id": 1,
#   "author": {"id": 1, "username": "userA"},
#   "content": "My first post!",
#   "likes_count": 0,
#   "is_liked_by_user": false,
#   "comments_count": 0,
#   ...
# }

export POST_ID=1
```

#### Step 3: Like the Post

```bash
# User B likes User A's post
curl -X POST $API_URL/posts/$POST_ID/like/ \
  -H "Authorization: Token $TOKEN_B" \
  -H "Content-Type: application/json"

# Response (201 Created):
# {
#   "message": "Post liked successfully",
#   "likes_count": 1
# }
```

#### Step 4: Verify Like Count

```bash
# User A checks post (should show 1 like)
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/posts/$POST_ID/

# Response (200 OK):
# {
#   "likes_count": 1,
#   "is_liked_by_user": false,  # User A didn't like it (User B did)
#   ...
# }
```

#### Step 5: Check Notification

```bash
# User A checks notifications (should see like notification)
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/notifications/

# Response (200 OK):
# {
#   "count": 1,
#   "results": [
#     {
#       "id": 1,
#       "verb": "like",
#       "actor": {"id": 2, "username": "userB"},
#       "is_read": false,
#       ...
#     }
#   ]
# }
```

#### Step 6: Unlike the Post

```bash
# User B unlikes the post
curl -X POST $API_URL/posts/$POST_ID/unlike/ \
  -H "Authorization: Token $TOKEN_B" \
  -H "Content-Type: application/json"

# Response (200 OK):
# {
#   "message": "Post unliked successfully",
#   "likes_count": 0
# }
```

### Test Scenario 2: Comment & Reply Flow

```bash
# Step 1: User B comments on User A's post
curl -X POST $API_URL/posts/$POST_ID/comment/ \
  -H "Authorization: Token $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great post!"}'

# Response (201 Created):
# {
#   "id": 1,
#   "author": {"username": "userB"},
#   "content": "Great post!",
#   "parent_comment": null,
#   "is_reply": false,
#   ...
# }

export COMMENT_ID=1

# Step 2: Get comments (should see User B's comment)
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/posts/$POST_ID/comments/

# Response includes User B's comment

# Step 3: User A replies to the comment
curl -X POST $API_URL/posts/$POST_ID/comment/ \
  -H "Authorization: Token $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Thanks!",
    "parent_comment": '$COMMENT_ID'
  }'

# Response (201 Created):
# {
#   "id": 2,
#   "parent_comment": 1,
#   "is_reply": true,
#   ...
# }

# Step 4: Get comments again (reply should nest under original)
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/posts/$POST_ID/comments/

# Response shows comment 1 with reply 2 nested in "replies" field
```

### Test Scenario 3: Notification Preferences

```bash
# Step 1: Get current preferences
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/preferences/

# Response shows all notifications enabled by default

# Step 2: Disable like notifications
curl -X PATCH $API_URL/preferences/ \
  -H "Authorization: Token $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"like_notifications": false}'

# Response (200 OK) with updated preferences

# Step 3: User B likes User A's post (but preference is disabled)
curl -X POST $API_URL/posts/$POST_ID/like/ \
  -H "Authorization: Token $TOKEN_B" \
  -H "Content-Type: application/json"

# Response (201 Created) - like succeeds

# Step 4: Verify no notification created
curl -H "Authorization: Token $TOKEN_A" \
  "$API_URL/notifications/?verb=like"

# Response shows NO like notifications
```

### Test Scenario 4: Bulk Operations

```bash
# Get multiple notification IDs first
curl -H "Authorization: Token $TOKEN_A" \
  "$API_URL/notifications/"

# Extract IDs, then bulk mark as read
curl -X POST $API_URL/notifications/bulk_action/ \
  -H "Authorization: Token $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_ids": [1, 2, 3],
    "action": "mark_read"
  }'

# Response (200 OK):
# {
#   "message": "Marked 3 notification(s) as read",
#   "count": 3
# }

# Verify all unread count is now 0
curl -H "Authorization: Token $TOKEN_A" \
  $API_URL/notifications/unread_count/

# Response:
# {
#   "unread_count": 0
# }
```

---

## Part 3: Postman Testing

### Setup Postman

1. **Import Collection**
   - Open Postman
   - Click "Import"
   - Select [Postman_Collection.json](Postman_Collection.json)

2. **Set Environment Variables**
   - Click "Environment" (gear icon)
   - Create new environment
   - Set variables:
     - `base_url`: `http://localhost:8000`
     - `token`: (leave blank, will populate after login)

3. **Configure API Base URL**
   - All requests use: `{{base_url}}/api/...`
   - Token used as: `Authorization: Token {{token}}`

### Test Execution in Postman

#### Step 1: Register & Login

1. Go to "Authentication" folder
2. Click "Register User" request
3. Send request (should return 201 Created)
4. Copy token from response
5. Set environment variable `token` to copied value
6. Verify login with "Login User" request

#### Step 2: Test Like Functionality

1. Go to "Like Functionality" folder
2. Execute in order:
   - "Like a Post" (should return 201)
   - "Like a Post" again (should return 400 - already liked)
   - "Unlike a Post" (should return 200)
   - "Unlike a Post" again (should return 400 - not liked)

#### Step 3: Test Comments & Replies

1. Go to "Comments & Replies" folder
2. Execute in order:
   - "Add Comment" (returns 201)
   - Copy comment ID from response
   - Edit "Reply to Comment" with correct parent_comment ID
   - "Reply to Comment" (returns 201)
   - "Get Comments" (shows comment with nested reply)

#### Step 4: Test Notifications

1. Go to "Notifications" folder
2. Execute requests in order:
   - "List Notifications" (200)
   - "Get Unread Count" (shows count)
   - "Mark Single as Read" (200)
   - "Mark All as Read" (200)
   - "Bulk Action - Mark Read" (200)
   - "Clear All Notifications" (200)

#### Step 5: Test Preferences

1. Go to "Preferences" folder
2. Execute requests:
   - "Get Preferences" (shows current settings)
   - "Update Preferences - Disable Likes" (200)
   - Verify likes can still be created
   - Verify notifications NOT created for likes
   - "Update Preferences - Enable Email" (200)
   - Continue with other preference updates

### Using Postman Scripts

#### Pre-request Script (Auto-populate IDs)

```javascript
// Save post ID from previous response
pm.environment.set("post_id", pm.response.json().id);
```

#### Tests Script (Verify Responses)

```javascript
// Verify status code
pm.test("Status is 201", function() {
    pm.response.to.have.status(201);
});

// Verify response structure
pm.test("Response has message", function() {
    pm.expect(pm.response.json().message).to.exist;
});

// Save token for future requests
pm.test("Token received", function() {
    var token = pm.response.json().token;
    pm.environment.set("token", token);
});
```

---

## Part 4: Integration Testing Scenarios

### Scenario 1: Multi-User Interaction

**Objective**: Test system with multiple users liking, commenting, and replying

```
Timeline:
T1: User A creates Post P1
T2: User B likes Post P1
    → Notification N1 created for User A
T3: User C likes Post P1
    → Notification N2 created for User A
T4: User B comments on Post P1
    → Notification N3 created for User A
T5: User C replies to User B's comment
    → Notification N4 created for User B (reply)
    → Notification N5 created for User A (comment on post)
```

**Test Steps**:
1. Create 3 test users (A, B, C)
2. Execute timeline above
3. Verify:
   - User A has 4 unread notifications
   - User B has 1 unread notification (reply)
   - All notifications have correct verb/actor

### Scenario 2: Preference-Based Notification Filtering

**Objective**: Verify preferences prevent unwanted notifications

```
Preferences:
- User A: like_notifications = false
- User A: comment_notifications = true
```

**Test Steps**:
1. Have User B like User A's post
   - Verify NO notification created (preference disabled)
2. Have User C comment on User A's post
   - Verify notification created (preference enabled)
3. Toggle preferences
   - Verify new behavior respected

### Scenario 3: Bulk Operations Performance

**Objective**: Verify bulk operations work efficiently

**Test Steps**:
1. Create 50+ notifications for User A
2. Mark first 20 as read (single operations)
   - Record time T1
3. Mark remaining 30+ as read (bulk operation)
   - Record time T2
4. Verify T2 is significantly faster than 30 single operations would be

### Scenario 4: Concurrency Testing

**Objective**: Verify system handles concurrent requests

```
Parallel Requests:
- User B likes Post P1
- User C likes Post P1
- User D comments on Post P1
All simultaneously
```

**Test Steps**:
1. Use thread pool or concurrent requests
2. Send multiple operations in parallel
3. Verify all succeed without race conditions
4. Check all notifications created correctly

---

## Part 5: Error Scenario Testing

### Test Duplicate Like

```bash
# Attempt 1: Success
curl -X POST $API_URL/posts/1/like/ \
  -H "Authorization: Token $TOKEN"
# Expected: 201 Created

# Attempt 2: Fail
curl -X POST $API_URL/posts/1/like/ \
  -H "Authorization: Token $TOKEN"
# Expected: 400 Bad Request
# Error message: "already liked this post"
```

### Test Invalid Parent Comment

```bash
curl -X POST $API_URL/posts/1/comment/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Reply",
    "parent_comment": 999
  }'

# Expected: 400 Bad Request
# Error message: "Parent comment not found"
```

### Test Unauthorized Access

```bash
# Without authentication
curl -H "Authorization: Token invalid_token" \
  $API_URL/notifications/

# Expected: 401 Unauthorized
# Error: "Invalid token"
```

### Test Missing Required Fields

```bash
# Comment without content
curl -X POST $API_URL/posts/1/comment/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected: 400 Bad Request
# Error: "content is required"
```

---

## Part 6: Performance Testing

### Query Optimization Verification

```bash
# Check number of queries executed
python manage.py shell

from django.db import connection
from django.test.utils import CaptureQueriesContext
from notifications.models import Notification

with CaptureQueriesContext(connection) as ctx:
    notifications = list(Notification.objects.filter(
        recipient_id=1
    ).select_related('actor', 'content_type'))

print(f"Queries executed: {len(ctx)}")
# Expected: 2-3 queries max (not N+1)
```

### Response Time Measurement

```bash
# Measure notification list endpoint
time curl -H "Authorization: Token $TOKEN" \
  $API_URL/notifications/

# Expected: < 200ms
```

### Load Testing (with Apache Bench)

```bash
# Install ab (Apache Bench)
# Ubuntu: apt-get install apache2-utils
# macOS: brew install ab

# Run 100 requests with 10 concurrent
ab -n 100 -c 10 -H "Authorization: Token $TOKEN" \
  $API_URL/notifications/

# Analyze results
# - Requests per second should be >100
# - Failed requests should be 0
# - Mean time per request should be <50ms
```

---

## Testing Checklist

### Pre-Testing
- [x] Database migrations applied
- [x] Django development server running
- [x] Test user accounts created
- [x] Authentication tokens obtained
- [x] Postman collection imported (if using Postman)

### Like Functionality
- [x] Can like a post (201 Created)
- [x] Cannot like twice (400 Bad Request)
- [x] Can unlike a post (200 OK)
- [x] Cannot unlike if not liked (400 Bad Request)
- [x] Like count accurate
- [x] Multiple users can like same post
- [x] Self-likes don't create notifications

### Comments
- [x] Can add comments (201 Created)
- [x] Can reply to comments (201 Created)
- [x] Replies nest under parent comment
- [x] Comment count accurate
- [x] Nested replies show in "replies" field

### Notifications
- [x] Like creates notification
- [x] Comment creates notification
- [x] Reply creates notification (to commenter)
- [x] Notifications can be listed
- [x] Can filter by unread status
- [x] Can filter by verb (like, comment, etc)
- [x] Can mark single as read
- [x] Can mark all as read
- [x] Can get unread count
- [x] Can bulk operate on notifications
- [x] Can delete all notifications

### Preferences
- [x] Can get preferences
- [x] Can update preferences
- [x] Preferences prevent notifications
- [x] Email notification toggles work
- [x] Preferences auto-created

### Authentication & Authorization
- [x] Unauthenticated requests rejected
- [x] Invalid tokens rejected
- [x] Users can only access own notifications
- [x] Users can only update own preferences

### Edge Cases
- [x] Comment on deleted post
- [x] Reply to deleted comment
- [x] Like deleted post
- [x] Bulk operations with invalid IDs
- [x] Concurrent likes on same post
- [x] Many nested replies

---

## Troubleshooting

| | Issue | Cause | Solution |
|---|-------|-------|----------|
| 1 | 404 Not Found on `/api/posts/1/like/` | URL not routed | Verify PostViewSet @action decorator |
| 2 | 401 Unauthorized | Missing authentication | Add `Authorization: Token` header |
| 3 | Notifications not creating | Signal not importing | Check `notifications/apps.py` |
| 4 | Duplicate likes allowed | Unique constraint not applied | Run migrations |
| 5 | Tests fail with ImportError | App not in INSTALLED_APPS | Add `'notifications'` to settings |

---

## Success Criteria

✅ **All tests pass**
- 21 automated tests pass
- No manual testing errors
- All cURL commands return expected status codes

✅ **System Reliability**
- No duplicate likes created
- No orphaned notifications
- Preferences properly enforced
- No N+1 query problems

✅ **Performance**
- List notifications: < 200ms
- Like post: < 100ms
- Mark all as read: < 500ms

---

**Date Last Updated**: February 21, 2026  
**Coverage**: Complete Like & Notification System  
**Status**: ✅ Ready for Production
