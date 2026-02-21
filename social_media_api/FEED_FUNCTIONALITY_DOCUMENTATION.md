# Feed Functionality - Implementation Documentation

## Overview
This document describes the feed functionality implemented in the social_media_api. The feed feature enables users to view posts from other users they follow, creating a personalized content experience.

## Requirements & Components

### Step 3: Feed Generation ✅
- Created a feed view that generates posts based on followed users
- Posts are ordered by creation date (most recent first)
- Feed is personalized for each authenticated user

### Step 4: URL Patterns ✅
- Set up URL patterns for follow management in `accounts/urls.py`
- Added routes for the feed endpoint in `posts/urls.py`

---

## Database Models

### Post Model
Represents a social media post created by a user.

```python
class Post(models.Model):
    author = ForeignKey(User)           # Who created this post
    content = TextField(max_length=5000) # Post content
    image = ImageField()                 # Optional image
    created_at = DateTimeField()        # Creation timestamp
    updated_at = DateTimeField()        # Last update timestamp
```

**Fields:**
- `author`: Foreign key to CustomUser (CASCADE delete)
- `content`: Text content (up to 5000 characters)
- `image`: Optional image upload
- `created_at`: Auto-set on creation
- `updated_at`: Auto-updated on modification

**Indexes:**
- `-created_at` (for ordering)
- `['author', '-created_at']` (for user-specific posts)

### Like Model
Represents a user liking a post.

```python
class Like(models.Model):
    user = ForeignKey(User)     # Who liked
    post = ForeignKey(Post)     # Which post was liked
    created_at = DateTimeField() # When the like was created
```

**Constraints:**
- `unique_together = ('user', 'post')` - User can only like a post once

### Comment Model
Represents a comment on a post.

```python
class Comment(models.Model):
    author = ForeignKey(User)     # Who commented
    post = ForeignKey(Post)       # Which post
    content = TextField(max_length=1000) # Comment text
    created_at = DateTimeField()  # Creation timestamp
    updated_at = DateTimeField()  # Last update timestamp
```

---

## API Endpoints

### Feed Endpoints

#### 1. Get Personalized Feed
**Endpoint:** `GET /api/feed/`

**Authentication:** Required (Token)

**Description:** Returns posts from users that the current user follows, ordered by creation date (most recent first).

**Response (200 OK):**
```json
{
    "count": 15,
    "posts": [
        {
            "id": 5,
            "author": {
                "id": 2,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Software Engineer",
                "profile_picture": "http://example.com/media/profile_pictures/john.jpg",
                "is_following": true
            },
            "content": "Just finished a great project!",
            "image": null,
            "likes_count": 5,
            "is_liked_by_user": false,
            "comments_count": 2,
            "created_at": "2026-02-21T10:30:00Z",
            "updated_at": "2026-02-21T10:30:00Z"
        },
        {
            "id": 4,
            "author": {
                "id": 3,
                "username": "alice",
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
                "bio": "Designer",
                "profile_picture": null,
                "is_following": true
            },
            "content": "New design mockup ready for review",
            "image": "http://example.com/media/post_images/design.jpg",
            "likes_count": 12,
            "is_liked_by_user": true,
            "comments_count": 5,
            "created_at": "2026-02-21T09:15:00Z",
            "updated_at": "2026-02-21T09:15:00Z"
        }
    ]
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/feed/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Query Parameters:**
- `page` - Page number for pagination (if implemented)
- `page_size` - Posts per page (if implemented)

---

#### 2. Get User-Specific Feed
**Endpoint:** `GET /api/feed/<username>/`

**Authentication:** Optional

**Description:** Returns all posts from a specific user.

**Response (200 OK):**
```json
{
    "count": 8,
    "username": "john_doe",
    "posts": [
        {
            "id": 5,
            "author": { ... },
            "content": "Just finished a great project!",
            "image": null,
            "likes_count": 5,
            "is_liked_by_user": false,
            "comments_count": 2,
            "created_at": "2026-02-21T10:30:00Z",
            "updated_at": "2026-02-21T10:30:00Z"
        }
    ]
}
```

**Error Response (404 Not Found):**
```json
{"error": "User john_doe not found or has no posts."}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/feed/john_doe/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

#### 3. Explore Posts
**Endpoint:** `GET /api/explore/`

**Authentication:** Optional

**Description:** Returns recent posts from all users (up to 50 most recent), useful for discovering new content.

**Response (200 OK):**
```json
{
    "count": 50,
    "posts": [
        {
            "id": 23,
            "author": { ... },
            "content": "Exploring new technologies",
            ...
        }
    ]
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/explore/
```

---

### Post Management Endpoints

#### 4. Create a Post
**Endpoint:** `POST /api/posts/`

**Authentication:** Required (Token)

**Request:**
```json
{
    "content": "This is my first post!",
    "image": null
}
```

**Response (201 Created):**
```json
{
    "id": 6,
    "author": { ... },
    "author_id": null,
    "content": "This is my first post!",
    "image": null,
    "likes": [],
    "likes_count": 0,
    "is_liked_by_user": false,
    "comments": [],
    "comments_count": 0,
    "created_at": "2026-02-21T11:00:00Z",
    "updated_at": "2026-02-21T11:00:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is my first post!"}'
```

---

#### 5. Get a Specific Post
**Endpoint:** `GET /api/posts/<id>/`

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
    "id": 5,
    "author": { ... },
    "content": "Just finished a great project!",
    "image": null,
    "likes": [
        {
            "id": 1,
            "user": { ... },
            "created_at": "2026-02-21T10:35:00Z"
        }
    ],
    "likes_count": 5,
    "is_liked_by_user": true,
    "comments": [
        {
            "id": 1,
            "author": { ... },
            "content": "Great work!",
            "created_at": "2026-02-21T10:40:00Z",
            "updated_at": "2026-02-21T10:40:00Z"
        }
    ],
    "comments_count": 2,
    "created_at": "2026-02-21T10:30:00Z",
    "updated_at": "2026-02-21T10:30:00Z"
}
```

---

#### 6. Update a Post
**Endpoint:** `PUT/PATCH /api/posts/<id>/`

**Authentication:** Required (Token, must be post author)

**Request:**
```json
{
    "content": "Updated post content"
}
```

**Response (200 OK):** Updated post object

---

#### 7. Delete a Post
**Endpoint:** `DELETE /api/posts/<id>/`

**Authentication:** Required (Token, must be post author)

**Response (204 No Content)**

---

### Post Interaction Endpoints

#### 8. Like a Post
**Endpoint:** `POST /api/posts/<id>/like/`

**Authentication:** Required (Token)

**Request:** `{}`

**Response (201 Created):**
```json
{
    "message": "Post liked successfully",
    "likes_count": 6
}
```

**Error Response (400 Bad Request):**
```json
{"error": "You have already liked this post."}
```

---

#### 9. Unlike a Post
**Endpoint:** `POST /api/posts/<id>/unlike/`

**Authentication:** Required (Token)

**Request:** `{}`

**Response (200 OK):**
```json
{
    "message": "Post unliked successfully",
    "likes_count": 5
}
```

**Error Response (400 Bad Request):**
```json
{"error": "You have not liked this post."}
```

---

#### 10. Add a Comment
**Endpoint:** `POST /api/posts/<id>/comment/`

**Authentication:** Required (Token)

**Request:**
```json
{
    "content": "Great post!"
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "author": {
        "id": 1,
        "username": "current_user",
        "email": "user@example.com",
        "first_name": "User",
        "last_name": "Name",
        "bio": "My bio",
        "profile_picture": null,
        "is_following": false
    },
    "author_id": null,
    "content": "Great post!",
    "created_at": "2026-02-21T11:05:00Z",
    "updated_at": "2026-02-21T11:05:00Z"
}
```

---

#### 11. Get Post Comments
**Endpoint:** `GET /api/posts/<id>/comments/`

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
    "count": 2,
    "comments": [
        {
            "id": 1,
            "author": { ... },
            "content": "Great work!",
            "created_at": "2026-02-21T10:40:00Z",
            "updated_at": "2026-02-21T10:40:00Z"
        },
        {
            "id": 2,
            "author": { ... },
            "content": "Thanks!",
            "created_at": "2026-02-21T10:45:00Z",
            "updated_at": "2026-02-21T10:45:00Z"
        }
    ]
}
```

---

#### 12. Get User Posts
**Endpoint:** `GET /api/posts/user_posts/?username=john_doe`

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
    "count": 8,
    "username": "john_doe",
    "posts": [ ... ]
}
```

---

### Follow Management Endpoints

#### 13. Follow a User
**Endpoint:** `POST /api/auth/follow/<user_id>/`

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
    "message": "You are now following john_doe",
    "status": "following",
    "user": {
        "id": 2,
        "username": "john_doe"
    },
    "followers_count": 5
}
```

---

#### 14. Unfollow a User
**Endpoint:** `POST /api/auth/unfollow/<user_id>/`

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
    "message": "You have unfollowed john_doe",
    "status": "not_following",
    "followers_count": 4
}
```

---

## URL Patterns Summary

### Accounts URLs (`/api/auth/`)
```
POST   /register/                      - Register new user
POST   /login/                         - Login user
POST   /logout/                        - Logout user
GET    /profile/                       - Get current user profile
GET    /users/<id>/                    - Get user by ID
POST   /follow/<user_id>/              - Follow user
POST   /unfollow/<user_id>/            - Unfollow user
POST   /users/<user_id>/follow/        - Follow user (alt)
POST   /users/<user_id>/unfollow/      - Unfollow user (alt)
```

### Posts URLs (`/api/`)
```
GET    /feed/                          - Get personalized feed
GET    /feed/<username>/               - Get user's feed
GET    /explore/                       - Explore recent posts
GET    /feed-alt/                      - Alternative feed endpoint
POST   /posts/                         - Create post
GET    /posts/                         - List all posts
GET    /posts/<id>/                    - Get specific post
PUT    /posts/<id>/                    - Update post
DELETE /posts/<id>/                    - Delete post
POST   /posts/<id>/like/               - Like post
POST   /posts/<id>/unlike/             - Unlike post
POST   /posts/<id>/comment/            - Add comment
GET    /posts/<id>/comments/           - Get post comments
GET    /posts/user_posts/              - Get user posts (query: username)
```

---

## Serializers

### PostSerializer
- Full post details with author, likes, comments
- Used for detailed post view
- Includes `is_liked_by_user` indicator

### FeedPostSerializer
- Lightweight post details (no nested likes/comments objects)
- Used for feed listings
- Optimized for performance
- Includes like/comment counts

### PostCreateSerializer
- Simplified form for creating posts
- Only accepts `content` and optional `image`
- Automatically sets author to current user

### CommentSerializer
- For displaying and creating comments
- Includes author information

### LikeSerializer
- For displaying likes on a post
- Includes user information

### AuthorSerializer
- User information for posts/comments
- Includes `is_following` indicator

---

## Performance Optimizations

### QuerySet Optimization
All feed views use `select_related()` and `prefetch_related()` to minimize database queries:
```python
queryset = Post.objects.select_related(
    'author'
).prefetch_related(
    'likes',
    'comments'
).order_by('-created_at')
```

### Database Indexes
- Posts indexed on `-created_at` for fast ordering
- Posts indexed on `['author', '-created_at']` for user-specific queries
- Comments indexed on `['post', '-created_at']` for comment retrieval

### Denormalized Fields
- Like and comment counts are calculated on-demand
- Can be denormalized in the future for better performance

---

## Usage Examples

### Python Requests
```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get feed
resp = requests.get(f"{BASE_URL}/feed/", headers=headers)
feed = resp.json()
print(f"Posts in feed: {feed['count']}")

# Create post
post_data = {"content": "Hello world!"}
resp = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
new_post = resp.json()
print(f"Created post: {new_post['id']}")

# Like a post
resp = requests.post(f"{BASE_URL}/posts/1/like/", headers=headers)
result = resp.json()
print(result['message'])

# Add comment
comment_data = {"content": "Great post!"}
resp = requests.post(f"{BASE_URL}/posts/1/comment/", json=comment_data, headers=headers)
comment = resp.json()
print(f"Added comment: {comment['id']}")
```

### JavaScript/fetch
```javascript
const token = "your_auth_token";
const BASE_URL = "http://localhost:8000/api";

// Get feed
fetch(`${BASE_URL}/feed/`, {
    headers: {"Authorization": `Token ${token}`}
})
.then(r => r.json())
.then(data => console.log(`Posts: ${data.count}`));

// Create post
fetch(`${BASE_URL}/posts/`, {
    method: "POST",
    headers: {
        "Authorization": `Token ${token}`,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({content: "Hello world!"})
})
.then(r => r.json())
.then(data => console.log(`Created post: ${data.id}`));

// Like a post
fetch(`${BASE_URL}/posts/1/like/`, {
    method: "POST",
    headers: {"Authorization": `Token ${token}`}
})
.then(r => r.json())
.then(data => console.log(data.message));
```

---

## Testing

### Setup for Testing
1. Create test users using registration endpoint
2. Have users follow each other
3. Create posts for each user
4. Test feed generation

### Test Scenarios

**Scenario 1: Personalized Feed**
1. User A follows User B and User C
2. Users B and C create posts
3. User A calls `/api/feed/`
4. Verify posts from B and C appear, sorted by creation date

**Scenario 2: Empty Feed**
1. New User D doesn't follow anyone
2. User D calls `/api/feed/`
3. Verify empty feed response

**Scenario 3: Post Interactions**
1. User A creates a post
2. User B likes the post
3. User C adds a comment
4. Verify like and comment counts update

**Scenario 4: User Feed**
1. Access `/api/feed/john_doe/`
2. Verify only john_doe's posts appear

---

## Integration with Follow Feature

The feed feature integrates seamlessly with the follow feature:
- Users can only see posts from users they follow
- The feed is dynamically updated based on follow/unfollow actions
- Feed shows accurate like/comment counts

---

## Notes & Best Practices

✅ Always authenticate when accessing personal feed
✅ Feed endpoint handles empty results gracefully
✅ Database queries are optimized for performance
✅ Proper error handling for edge cases
✅ Consistent JSON response formatting
✅ Author information includes follow status

---

## Future Enhancements

- [ ] Pagination for large feeds
- [ ] Caching for improved performance
- [ ] Real-time feed updates (WebSocket)
- [ ] Feed filters (by date, likes, etc.)
- [ ] Trending posts algorithm
- [ ] Search functionality
- [ ] Post recommendations
- [ ] Hashtag support
- [ ] Mention functionality (@username)
- [ ] Repost/share feature
