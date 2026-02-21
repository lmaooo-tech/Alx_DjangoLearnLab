# Follow Feature - Developer Quick Reference

## 📋 Quick API Reference

### Follow a User
```
POST /api/users/{user_id}/follow/
Authorization: Token {YOUR_TOKEN}

Response (200):
{
    "message": "You are now following john_doe",
    "status": "following",
    "user": {"id": 2, "username": "john_doe"},
    "followers_count": 5
}
```

### Unfollow a User
```
POST /api/users/{user_id}/unfollow/
Authorization: Token {YOUR_TOKEN}

Response (200):
{
    "message": "You have unfollowed john_doe",
    "status": "not_following",
    "followers_count": 4
}
```

### Get User's Followers
```
GET /api/users/{user_id}/followers/
Authorization: Token {YOUR_TOKEN}

Response (200):
{
    "count": 5,
    "user": "john_doe",
    "followers": [
        {"id": 1, "username": "alice", "is_following": true},
        {"id": 3, "username": "bob", "is_following": false}
    ]
}
```

### Get User's Following List
```
GET /api/users/{user_id}/following/
Authorization: Token {YOUR_TOKEN}

Response (200):
{
    "count": 3,
    "user": "john_doe",
    "following": [...]
}
```

### Get My Followers
```
GET /api/users/my_followers/
Authorization: Token {YOUR_TOKEN}
```

### Get My Following
```
GET /api/users/my_following/
Authorization: Token {YOUR_TOKEN}
```

---

## 🗂️ File Structure

```
accounts/
├── models.py              # CustomUser with followers field (UNCHANGED)
├── serializers.py         # +4 new serializers for follow features
├── views.py              # +6 action methods in UserViewSet + 2 new views
├── urls.py               # +2 new URL patterns
├── migrations/
│   └── 0001_initial.py   # Contains followers ManyToMany field (UNCHANGED)
└── ...
```

---

## 🔑 Key Implementation Details

### Model Relationship
```python
# In CustomUser model
followers = models.ManyToManyField(
    'self',
    symmetrical=False,      # Unidirectional
    related_name='following'
)

# Usage:
user.followers.all()      # Who follows this user
user.following.all()      # Who this user follows
```

### ViewSet Actions
```python
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    # Custom actions use @action decorator
    @action(detail=True, methods=['post'])
    def follow(self, request, id=None):
        # Follow logic
        
    @action(detail=False, methods=['get'])
    def my_following(self, request):
        # Get current user's following
```

### Error Codes & Responses
| Scenario | Status | Response |
|----------|--------|----------|
| Try to follow yourself | 400 | `{"error": "You cannot follow yourself."}` |
| Already following | 400 | `{"error": "You are already following this user."}` |
| Not following when unfollow | 400 | `{"error": "You are not following this user."}` |
| User doesn't exist | 404 | `{"error": "User not found."}` |
| Success | 200 | `{"message": "...", "status": "..."}` |

---

## 🧪 Testing Checklist

### Manual Testing
- [ ] Register 2 users
- [ ] User A follows User B
- [ ] Verify User A appears in User B's followers
- [ ] Verify User B appears in User A's following
- [ ] User A unfollows User B
- [ ] Verify relationship is removed
- [ ] Test self-follow prevention (400 error)
- [ ] Test duplicate follow prevention (400 error)
- [ ] Test unfollow when not following (400 error)

### API Testing
- [ ] Follow endpoint requires authentication
- [ ] Unfollow endpoint requires authentication
- [ ] Followers list shows correct count
- [ ] Following list shows correct count
- [ ] is_following field shows correct state

---

## 💻 Common Django ORM Queries

```python
from accounts.models import CustomUser

# Get a user
user = CustomUser.objects.get(username='john_doe')

# Get user's followers
followers = user.followers.all()
followers_count = user.followers.count()

# Get users this user follows
following = user.following.all()
following_count = user.following.count()

# Check if user A follows user B
user_a = CustomUser.objects.get(username='alice')
user_b = CustomUser.objects.get(username='bob')
follows = user_a.following.filter(id=user_b.id).exists()

# Get all followers of a user (reverse lookup)
followers_of_john = john.followers.all()

# Follow a user (adds the follower)
target_user.followers.add(follower_user)

# Unfollow a user (removes the follower)
target_user.followers.remove(follower_user)

# Get mutual followers
mutual = user_a.followers.filter(following=user_b)

# Get all users not followed by a user
not_following = CustomUser.objects.exclude(followers=user_a)
```

---

## 🐛 Troubleshooting

### Issue: Follow action not working
- **Check:** User is authenticated (has valid token)
- **Check:** User IDs are correct
- **Check:** Target user exists in database

### Issue: Followers/Following list is empty
- **Check:** Users have been followed/unfollowed properly
- **Check:** Correct user ID is in the URL
- **Check:** User making request is authenticated

### Issue: Can't follow/unfollow
- **Verify:** You're not trying to follow yourself
- **Verify:** You're using correct HTTP method (POST)
- **Verify:** You have valid authentication token

---

## 📚 Related Documentation Files

- `FOLLOW_FEATURE_DOCUMENTATION.md` - Complete API documentation
- `FOLLOW_IMPLEMENTATION_SUMMARY.md` - Implementation overview
- [This file] - Developer quick reference

---

## 🚀 Future Integration Points

The follow feature works standalone but is designed to integrate with:
1. **Dynamic Feed** - Show posts from followed users
2. **Notifications** - Notify users of new followers
3. **User Recommendations** - Suggest users to follow
4. **Blocking System** - Prevent certain users from following
5. **Analytics** - Track follower growth

---

## 📝 Code Examples

### Follow/Unfollow with Python
```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_token"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Follow user ID 2
resp = requests.post(f"{BASE_URL}/users/2/follow/", headers=HEADERS)
print(resp.json())

# Get followers
resp = requests.get(f"{BASE_URL}/users/2/followers/", headers=HEADERS)
print(resp.json())
```

### Follow/Unfollow with JavaScript
```javascript
const token = "your_token";
const BASE_URL = "http://localhost:8000/api";

// Follow user
fetch(`${BASE_URL}/users/2/follow/`, {
    method: "POST",
    headers: {"Authorization": `Token ${token}`}
})
.then(r => r.json())
.then(d => console.log(d));

// Get followers
fetch(`${BASE_URL}/users/2/followers/`, {
    headers: {"Authorization": `Token ${token}`}
})
.then(r => r.json())
.then(d => console.log(d));
```

---

## 🔐 Security Notes

✅ All endpoints require authentication
✅ Users can only modify their own follow status
✅ Self-follows are prevented
✅ Duplicate follows are prevented
✅ User existence is validated
✅ Proper error messages without data leakage
