# Social Media API - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1️⃣ Start the Server

```bash
cd social_media_api
python manage.py runserver
```

Server runs at: `http://localhost:8000`

---

## 2️⃣ Register Your First Account

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

**Save the token returned:**
```bash
TOKEN="abc123def456..."
USER_ID=1
```

---

## 3️⃣ Create More Users

```bash
# Create bob
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "email": "bob@example.com",
    "password": "password123",
    "password_confirm": "password123"
  }'

# Create charlie
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "charlie",
    "email": "charlie@example.com",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

---

## 4️⃣ Follow Users

As Alice, follow Bob (assuming Bob's ID is 2):

```bash
curl -X POST http://localhost:8000/api/auth/follow/2/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
    "message": "You are now following bob",
    "status": "following"
}
```

---

## 5️⃣ Create Posts

As Bob, create a post (use Bob's token):

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello everyone! This is my first post."
  }'
```

**Response:**
```json
{
    "id": 1,
    "author": {
        "id": 2,
        "username": "bob",
        "email": "bob@example.com"
    },
    "content": "Hello everyone! This is my first post.",
    "likes_count": 0,
    "comments_count": 0,
    "created_at": "2026-02-21T12:00:00Z"
}
```

---

## 6️⃣ View Your Feed

As Alice (who follows Bob), view your personalized feed:

```bash
curl -X GET http://localhost:8000/api/feed/ \
  -H "Authorization: Token $ALICE_TOKEN"
```

**Result:** Shows Bob's post (since Alice follows Bob)

---

## 7️⃣ Like a Post

Like Bob's post:

```bash
curl -X POST http://localhost:8000/api/posts/1/like/ \
  -H "Authorization: Token $ALICE_TOKEN"
```

**Response:**
```json
{
    "message": "Post liked successfully",
    "likes_count": 1
}
```

---

## 8️⃣ Add a Comment

Comment on Bob's post:

```bash
curl -X POST http://localhost:8000/api/posts/1/comment/ \
  -H "Authorization: Token $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post, Bob!"
  }'
```

---

## 📚 Core Endpoints

### Authentication
```bash
POST   /api/auth/register/          # Register
POST   /api/auth/login/              # Login
GET    /api/auth/profile/            # Your profile
PATCH  /api/auth/profile/            # Update profile
```

### Follow
```bash
POST   /api/auth/follow/{id}/        # Follow user
POST   /api/auth/unfollow/{id}/      # Unfollow user
GET    /api/users/{id}/followers/    # View followers
GET    /api/users/{id}/following/    # View following
```

### Posts
```bash
POST   /api/posts/                   # Create post
GET    /api/posts/                   # List posts
GET    /api/posts/{id}/              # View post
PUT    /api/posts/{id}/              # Edit post
DELETE /api/posts/{id}/              # Delete post
```

### Feed
```bash
GET    /api/feed/                    # Your feed
GET    /api/feed/{username}/         # User's posts
GET    /api/explore/                 # All recent posts
```

### Interactions
```bash
POST   /api/posts/{id}/like/         # Like post
POST   /api/posts/{id}/unlike/       # Unlike post
POST   /api/posts/{id}/comment/      # Comment
GET    /api/posts/{id}/comments/     # Get comments
```

---

## 🔐 Authentication Pattern

Every request needs the token in the header:

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Get a token:**
1. Register: `POST /api/auth/register/` → returns token
2. Login: `POST /api/auth/login/` → returns token

---

## 📊 Common Workflows

### Workflow 1: User Discovery & Follow

```bash
# 1. List all users
curl -X GET http://localhost:8000/api/users/

# 2. Follow a user
curl -X POST http://localhost:8000/api/auth/follow/2/ \
  -H "Authorization: Token $TOKEN"

# 3. View their posts
curl -X GET http://localhost:8000/api/feed/bob/
```

### Workflow 2: Create & Share Post

```bash
# 1. Create post
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "My first post!"}'

# 2. Like your own post
curl -X POST http://localhost:8000/api/posts/1/like/ \
  -H "Authorization: Token $TOKEN"

# 3. Update post
curl -X PUT http://localhost:8000/api/posts/1/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content!"}'
```

### Workflow 3: Engage with Content

```bash
# 1. View feed
curl -X GET http://localhost:8000/api/feed/ \
  -H "Authorization: Token $TOKEN"

# 2. Like interesting post
curl -X POST http://localhost:8000/api/posts/5/like/ \
  -H "Authorization: Token $TOKEN"

# 3. Add comment
curl -X POST http://localhost:8000/api/posts/5/comment/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Love this!"}'

# 4. View all comments
curl -X GET http://localhost:8000/api/posts/5/comments/ \
  -H "Authorization: Token $TOKEN"
```

---

## 🎯 Key Concepts

### Personalized Feed
- Shows posts **only** from users you follow
- Newest posts appear first
- Empty if you don't follow anyone yet

### Follow System
- Follow is **one-way** (A can follow B without B following A)
- You cannot follow yourself
- You cannot follow the same person twice

### Likes
- Each user can like a post **only once**
- Duplicate likes are rejected
- Liking someone's post doesn't follow them

### Comments
- Any user can comment on any post
- Comments are ordered by creation date
- No limit on comments per post

---

## 📝 Response Format

All successful responses include:

```json
{
    "id": 1,
    "field1": "value",
    "field2": "value",
    "timestamps": "2026-02-21T12:00:00Z"
}
```

Error responses:

```json
{
    "error": "Error message here"
}
// or
{
    "detail": "Error details"
}
// or
{
    "field_name": ["Field validation error"]
}
```

---

## 🐛 Debugging Tips

### Check if token is valid
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token $TOKEN"
```

If you get 401, token is invalid.

### View all users
```bash
curl -X GET http://localhost:8000/api/users/
```

### Check your follows
```bash
curl -X GET http://localhost:8000/api/auth/my_following/ \
  -H "Authorization: Token $TOKEN"
```

### View a specific post
```bash
curl -X GET http://localhost:8000/api/posts/1/
```

---

## 🚨 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing/invalid token | Add valid token in Authorization header |
| 403 Forbidden | Not the post author | Can only edit/delete your own posts |
| 404 Not Found | Resource doesn't exist | Check ID is correct |
| 400 Bad Request | Invalid data | Check request format and field types |
| 500 Server Error | Server crash | Check Django logs |

---

## 📖 Full Documentation

- **Testing Guide:** `COMPREHENSIVE_TESTING_GUIDE.md` - 38 detailed tests
- **API Reference:** `API_COMPLETE_REFERENCE.md` - All endpoints
- **Database Design:** `MODEL_STRUCTURE_DESIGN.md` - Models & relationships
- **Project Summary:** `PROJECT_COMPLETION_SUMMARY.md` - Complete overview

---

## 🧪 Run Tests

### Using cURL Script
```bash
bash test_api.sh
```

### Using Postman
Import `POSTMAN_COLLECTION.json` into Postman

### Manual Testing
```bash
# Test feed endpoint
curl -X GET http://localhost:8000/api/feed/ \
  -H "Authorization: Token $TOKEN" | jq '.'
```

---

## 🔧 Admin Panel

Access Django admin:

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Go to: `http://localhost:8000/admin/`

3. Manage:
   - Users and followers
   - Posts and comments
   - Likes
   - All user data

---

## ⚡ Pro Tips

### Save Token to Variable
```bash
# Register and save token
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{...}')

TOKEN=$(echo $RESPONSE | jq -r '.token')
echo "Token: $TOKEN"
```

### Pretty Print JSON
```bash
curl ... | jq '.' # Requires jq installed
```

### Check HTTP Status
```bash
curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8000/api/posts/
# Returns: 200
```

### Save Response to File
```bash
curl ... > response.json
```

### Include Response Headers
```bash
curl -i http://localhost:8000/api/posts/
```

---

## 🎓 Learning Path

1. **Start Here:** Register and create accounts
2. **Follow System:** Follow some users, check followers list
3. **Posts:** Create posts, view posts from followed users
4. **Interactions:** Like and comment on posts
5. **Edition:** Edit and delete your own posts
6. **Permissions:** Try to delete someone else's post (should be forbidden)
7. **Feed:** Check that feed only shows followed users' posts
8. **Explore:** View explore page (all posts from everyone)

---

## 🆘 Getting Help

### Check Logs
```bash
python manage.py shell
>>> from posts.models import Post
>>> Post.objects.all()
```

### Django Shell
```bash
python manage.py shell

# Python commands
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(username='alice')
>>> user.following.all()  # Users alice follows
>>> user.followers.all()  # Users following alice
```

### Database Inspection
```bash
sqlite3 db.sqlite3
sqlite> SELECT * FROM accounts_customuser;
sqlite> .quit
```

---

### If stuck:
1. Check the endpoint is correct
2. Verify token is valid
3. Check response error message
4. Review detailed documentation files
5. Check Django server console for errors

---

## ✨ You're Ready!

You now have:
- ✅ Running social media API
- ✅ User follow system
- ✅ Personalized feeds
- ✅ Post management
- ✅ Like & comment system

**Next:** Read the full documentation for advanced usage patterns and complete endpoint reference.

Happy coding! 🎉
