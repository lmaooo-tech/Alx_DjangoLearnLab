# Feed Feature - Developer Quick Reference

## 🎯 Quick API Reference

### Get Your Personalized Feed
```
GET /api/feed/
Authorization: Token {YOUR_TOKEN}

Response (200):
{
    "count": 15,
    "posts": [
        {
            "id": 5,
            "author": {
                "username": "john_doe",
                "is_following": true
            },
            "content": "Just finished a great project!",
            "image": null,
            "likes_count": 5,
            "is_liked_by_user": false,
            "comments_count": 2,
            "created_at": "2026-02-21T10:30:00Z"
        },
        ...
    ]
}
```

### Create a Post
```
POST /api/posts/
Authorization: Token {YOUR_TOKEN}
Content-Type: application/json

Body:
{
    "content": "This is my first post!",
    "image": null
}

Response (201):
{
    "id": 6,
    "author": { ... },
    "content": "This is my first post!",
    "likes_count": 0,
    "comments_count": 0,
    ...
}
```

### Like a Post
```
POST /api/posts/{post_id}/like/
Authorization: Token {YOUR_TOKEN}

Response (201):
{
    "message": "Post liked successfully",
    "likes_count": 6
}
```

### Add a Comment
```
POST /api/posts/{post_id}/comment/
Authorization: Token {YOUR_TOKEN}
Content-Type: application/json

Body:
{
    "content": "Great post!"
}

Response (201):
{
    "id": 3,
    "author": { ... },
    "content": "Great post!",
    "created_at": "2026-02-21T11:05:00Z"
}
```

### Explore Recent Posts
```
GET /api/explore/

Response (200):
{
    "count": 50,
    "posts": [ ... ]
}
```

### Get User's Posts
```
GET /api/feed/{username}/

Response (200):
{
    "count": 8,
    "username": "john_doe",
    "posts": [ ... ]
}
```

---

## 🗂️ File Structure

```
posts/
├── models.py              # Post, Like, Comment models
├── serializers.py         # 6 serializers for API
├── views.py              # FeedView, PostViewSet, etc.
├── urls.py               # Feed and post URL patterns
├── admin.py              # Django admin config
├── apps.py               # App config
├── __init__.py           # Package init
└── migrations/
    └── 0001_initial.py   # Initial migration
```

---

## 📊 Database Models

### Post Model
```python
class Post(models.Model):
    author = ForeignKey(User)           # Who created
    content = TextField(max_length=5000) # Post content
    image = ImageField()                 # Optional image
    created_at = DateTimeField()        # Auto-created
    updated_at = DateTimeField()        # Auto-updated
```

### Like Model
```python
class Like(models.Model):
    user = ForeignKey(User)     # Who liked
    post = ForeignKey(Post)     # Which post
    created_at = DateTimeField() # When liked
    # unique_together: (user, post)
```

### Comment Model
```python
class Comment(models.Model):
    author = ForeignKey(User)          # Who commented
    post = ForeignKey(Post)            # Which post
    content = TextField(max_length=1000) # Comment text
    created_at = DateTimeField()       # Auto-created
    updated_at = DateTimeField()       # Auto-updated
```

---

## 🔄 Common Workflows

### Create Post → Like → Comment
```python
# 1. User creates a post
post_data = {"content": "Hello world!"}
post = create_post(post_data)

# 2. Another user likes it
like_post(post.id)

# 3. Another user comments
comment_data = {"content": "Great!"}
comment_on_post(post.id, comment_data)
```

### View Feed → Check Activity
```python
# 1. Get personalized feed
feed = get_feed()
# Returns posts from users you follow

# 2. View specific post details
post = get_post(post_id)
# Includes full likes and comments

# 3. Check if you liked it
is_liked = post.is_liked_by_user
# True if current user liked
```

---

## 🛠️ Development Setup

### Initialize Posts App
```bash
# Run migrations
python manage.py migrate posts

# Create superuser (for admin)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Django Shell Testing
```python
from posts.models import Post, Like, Comment
from accounts.models import CustomUser

# Get a user
user = CustomUser.objects.get(username='john_doe')

# Get posts by user
posts = user.posts.all()

# Get user's feed (posts from followed users)
following_ids = user.following.values_list('id', flat=True)
feed = Post.objects.filter(author_id__in=following_ids).order_by('-created_at')

# Get likes on a post
post = Post.objects.first()
like_count = post.likes.count()
liked_by_users = post.likes.values_list('user__username', flat=True)

# Get comments
comments = post.comments.all()
```

---

## 🔐 Permissions & Authentication

| Endpoint | Write | Read | Auth Required |
|----------|-------|------|---------------|
| GET /feed/ | - | Own feed | ✅ Yes |
| POST /posts/ | Own post | - | ✅ Yes |
| PUT /posts/<id>/ | Own post | - | ✅ Yes |
| DELETE /posts/<id>/ | Own post | - | ✅ Yes |
| POST /posts/<id>/like/ | - | - | ✅ Yes |
| POST /posts/<id>/comment/ | Own comment | - | ✅ Yes |
| GET /explore/ | - | Public | ❌ No |
| GET /feed/<username>/ | - | Public | ❌ No |

---

## 📈 API Endpoints Cheat Sheet

### Feed
```
GET    /api/feed/                              Get your feed
GET    /api/feed/<username>/                  Get user's posts
GET    /api/explore/                          Explore recent posts
```

### Posts
```
POST   /api/posts/                            Create post
GET    /api/posts/                            List posts
GET    /api/posts/<id>/                       Get post
PUT    /api/posts/<id>/                       Update post
DELETE /api/posts/<id>/                       Delete post
GET    /api/posts/user_posts/?username=       Get user posts
```

### Post Interactions
```
POST   /api/posts/<id>/like/                  Like post
POST   /api/posts/<id>/unlike/                Unlike post
POST   /api/posts/<id>/comment/               Add comment
GET    /api/posts/<id>/comments/              Get comments
```

### Follow Management
```
POST   /api/auth/follow/<user_id>/            Follow user
POST   /api/auth/unfollow/<user_id>/          Unfollow user
```

---

## 🧪 Test Scenarios

### Test 1: Feed Generation
1. User A follows User B
2. User B creates post
3. User A calls `/api/feed/`
4. Verify post appears

### Test 2: Post Interactions
1. Create post
2. Like post (verify count increases)
3. Add comment (verify count increases)
4. Unlike post (verify count decreases)

### Test 3: User Feed
1. User creates multiple posts
2. Call `/api/feed/username/`
3. Verify all posts appear
4. Verify sorted by newest first

### Test 4: Explore
1. Call `/api/explore/`
2. Verify recent posts from all users
3. Verify up to 50 posts returned

### Test 5: Error Cases
1. Try to like already-liked post (should error)
2. Try to comment with empty content (should error)
3. Try to update someone else's post (should error)

---

## 💻 Code Examples

### Python - Get Feed
```python
import requests

token = "your_auth_token"
headers = {"Authorization": f"Token {token}"}

response = requests.get(
    "http://localhost:8000/api/feed/",
    headers=headers
)
feed = response.json()

for post in feed['posts']:
    print(f"By: {post['author']['username']}")
    print(f"Content: {post['content']}")
    print(f"Likes: {post['likes_count']}")
    print("---")
```

### JavaScript - Create Post
```javascript
const token = "your_auth_token";

fetch("http://localhost:8000/api/posts/", {
    method: "POST",
    headers: {
        "Authorization": `Token ${token}`,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        content: "Hello world!",
        image: null
    })
})
.then(r => r.json())
.then(data => console.log(`Created post: ${data.id}`));
```

### Python - Like Post
```python
import requests

token = "your_auth_token"
post_id = 1
headers = {"Authorization": f"Token {token}"}

response = requests.post(
    f"http://localhost:8000/api/posts/{post_id}/like/",
    headers=headers
)
result = response.json()
print(f"Likes count: {result['likes_count']}")
```

---

## 🔍 Query Parameters

### Feed Pagination (when implemented)
```
GET /api/feed/?page=1&page_size=20
GET /api/feed/?page=2&page_size=10
```

### Get User Posts
```
GET /api/posts/user_posts/?username=john_doe
GET /api/posts/user_posts/?username=alice
```

---

## ⚡ Performance Tips

✅ Use `select_related` for author info (done)
✅ Use `prefetch_related` for likes/comments (done)
✅ Add database indexes (done)
✅ Use lightweight serializers for feed (done)
✅ Limit explore to 50 posts (done)

Future optimizations:
- Add pagination
- Implement caching
- Add WebSocket for real-time
- Denormalize counts

---

## 🔗 Related Files

- `FEED_FUNCTIONALITY_DOCUMENTATION.md` - Full API docs
- `FOLLOW_FEATURE_DOCUMENTATION.md` - Follow feature docs
- `FEED_IMPLEMENTATION_SUMMARY.md` - Implementation details

---

## 🐛 Troubleshooting

### Issue: Feed is empty
- **Check:** Are you following any users?
- **Check:** Have followed users created posts?
- **Solution:** Create posts as different users

### Issue: Can't create post
- **Check:** Are you authenticated?
- **Check:** Is content present in request?
- **Solution:** Verify token and request body

### Issue: Can't like post
- **Check:** Are you authenticated?
- **Check:** Have you already liked it?
- **Solution:** Check response error message

### Issue: Comment not appearing
- **Check:** Is post ID correct?
- **Check:** Is content in request body?
- **Solution:** Verify post exists and ID is valid

---

## 📝 Response Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET, POST (like), DELETE |
| 201 | Created | Successful POST (create) |
| 400 | Bad Request | Invalid input, duplicate like |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Trying to edit someone else's post |
| 404 | Not Found | Post/user doesn't exist |

---

## 🚀 Integration Checklist

- [x] Models created (Post, Like, Comment)
- [x] Serializers created (6 total)
- [x] Views created (FeedView, PostViewSet, etc.)
- [x] URLs configured
- [x] Migration created
- [x] Admin interface set up
- [x] Follow feature integrated
- [ ] Pagination implemented
- [ ] Caching added
- [ ] Tests written

---

## 📚 Database Schema at a Glance

```
CustomUser
  ├─ posts (ForeignKey Post.author)
  ├─ likes (ForeignKey Like.user)
  │   └─ related to posts
  ├─ comments (ForeignKey Comment.author)
  │   └─ related to posts
  └─ following (ManyToMany to self)

Post
  ├─ author (ForeignKey CustomUser)
  ├─ likes (reverse ForeignKey from Like)
  └─ comments (reverse ForeignKey from Comment)

Like
  ├─ user (ForeignKey CustomUser)
  └─ post (ForeignKey Post)

Comment
  ├─ author (ForeignKey CustomUser)
  └─ post (ForeignKey Post)
```

---

## ✨ Key Features

✅ **Personalized Feed** - See posts from users you follow
✅ **Post Management** - Create, edit, delete posts
✅ **Like System** - Like/unlike posts
✅ **Comments** - Comment on posts
✅ **Explore** - Browse recent posts
✅ **Performance** - Optimized queries
✅ **Security** - Proper authentication
✅ **Scalability** - Ready for future growth
