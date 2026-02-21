# User Follow/Unfollow Feature Documentation

## Overview
This document describes the user follow/unfollow feature implemented in the social_media_api. This feature enables users to follow and unfollow other users, managing user relationships in the social network.

## Model Structure

### CustomUser Model
The `CustomUser` model includes a self-referential many-to-many relationship:

```python
followers = models.ManyToManyField(
    'self',
    symmetrical=False,
    related_name='following',
    blank=True,
    help_text="Users who follow this user"
)
```

**Key Points:**
- `followers`: Users who follow this user
- `following` (related_name): Users that this user follows
- `symmetrical=False`: Allows unidirectional relationships (A follows B, but B doesn't automatically follow A)

## API Endpoints

### 1. Follow a User

**Endpoint:** `POST /api/auth/users/<user_id>/follow/`

**Alternative (via ViewSet):** `POST /api/users/<user_id>/follow/`

**Authentication:** Required (Token)

**Description:** Makes the authenticated user follow the specified user.

**Request:**
```json
{}
```

**Success Response (200 OK):**
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

**Error Responses:**

- **400 Bad Request** - Already following:
```json
{"error": "You are already following this user."}
```

- **400 Bad Request** - Trying to follow self:
```json
{"error": "You cannot follow yourself."}
```

- **404 Not Found** - User doesn't exist:
```json
{"error": "User not found."}
```

**cURL Example:**
```bash
curl -X POST \
  http://localhost:8000/api/auth/users/2/follow/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN' \
  -H 'Content-Type: application/json'
```

### 2. Unfollow a User

**Endpoint:** `POST /api/auth/users/<user_id>/unfollow/`

**Alternative (via ViewSet):** `POST /api/users/<user_id>/unfollow/`

**Authentication:** Required (Token)

**Description:** Makes the authenticated user unfollow the specified user.

**Request:**
```json
{}
```

**Success Response (200 OK):**
```json
{
    "message": "You have unfollowed john_doe",
    "status": "not_following",
    "user": {
        "id": 2,
        "username": "john_doe"
    },
    "followers_count": 4
}
```

**Error Responses:**

- **400 Bad Request** - Not following:
```json
{"error": "You are not following this user."}
```

- **400 Bad Request** - Trying to unfollow self:
```json
{"error": "You cannot unfollow yourself."}
```

- **404 Not Found** - User doesn't exist:
```json
{"error": "User not found."}
```

**cURL Example:**
```bash
curl -X POST \
  http://localhost:8000/api/auth/users/2/unfollow/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN' \
  -H 'Content-Type: application/json'
```

### 3. Get User's Followers

**Endpoint:** `GET /api/users/<user_id>/followers/`

**Authentication:** Required (Token)

**Description:** Retrieves a list of users who follow the specified user.

**Success Response (200 OK):**
```json
{
    "count": 5,
    "user": "john_doe",
    "followers": [
        {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "bio": "Tech enthusiast",
            "profile_picture": "http://example.com/media/profile_pictures/alice.jpg",
            "is_following": true
        },
        {
            "id": 3,
            "username": "bob",
            "email": "bob@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "bio": "Developer",
            "profile_picture": null,
            "is_following": false
        }
    ]
}
```

**Query Parameters:** None

**cURL Example:**
```bash
curl -X GET \
  http://localhost:8000/api/users/2/followers/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN'
```

### 4. Get User's Following List

**Endpoint:** `GET /api/users/<user_id>/following/`

**Authentication:** Required (Token)

**Description:** Retrieves a list of users that the specified user follows.

**Success Response (200 OK):**
```json
{
    "count": 3,
    "user": "john_doe",
    "following": [
        {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "bio": "Tech enthusiast",
            "profile_picture": "http://example.com/media/profile_pictures/alice.jpg",
            "is_following": false
        },
        {
            "id": 4,
            "username": "charlie",
            "email": "charlie@example.com",
            "first_name": "Charlie",
            "last_name": "Brown",
            "bio": "Designer",
            "profile_picture": null,
            "is_following": true
        }
    ]
}
```

**cURL Example:**
```bash
curl -X GET \
  http://localhost:8000/api/users/2/following/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN'
```

### 5. Get Current User's Followers

**Endpoint:** `GET /api/users/my_followers/`

**Authentication:** Required (Token)

**Description:** Retrieves a list of users who follow the authenticated user.

**Success Response (200 OK):**
```json
{
    "count": 5,
    "user": "current_user",
    "followers": [
        {
            "id": 2,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software engineer",
            "profile_picture": "http://example.com/media/profile_pictures/john.jpg",
            "is_following": true
        }
    ]
}
```

**cURL Example:**
```bash
curl -X GET \
  http://localhost:8000/api/users/my_followers/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN'
```

### 6. Get Current User's Following List

**Endpoint:** `GET /api/users/my_following/`

**Authentication:** Required (Token)

**Description:** Retrieves a list of users that the authenticated user follows.

**Success Response (200 OK):**
```json
{
    "count": 3,
    "user": "current_user",
    "following": [
        {
            "id": 2,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software engineer",
            "profile_picture": "http://example.com/media/profile_pictures/john.jpg",
            "is_following": false
        }
    ]
}
```

**cURL Example:**
```bash
curl -X GET \
  http://localhost:8000/api/users/my_following/ \
  -H 'Authorization: Token YOUR_AUTH_TOKEN'
```

## Serializers

### FollowSerializer
Used for follow/unfollow request validation:
- Validates `user_id` field
- Ensures the target user exists

### FollowingListSerializer
Used for displaying users being followed:
- Includes `is_following` field to show if the current user follows this user
- Displays user profile information

### FollowersListSerializer
Used for displaying user's followers:
- Includes `is_following` field
- Displays user profile information

### FollowActionResponseSerializer
Used for follow/unfollow action responses:
- Returns action message, status, and user information

## Views

### UserViewSet Actions

The `UserViewSet` includes the following custom actions:

1. **follow** (detail=True, POST)
   - Follow a specific user
   - Includes self-follow prevention

2. **unfollow** (detail=True, POST)
   - Unfollow a specific user
   - Includes self-unfollow prevention

3. **followers** (detail=True, GET)
   - List followers of a specific user

4. **following** (detail=True, GET)
   - List users followed by a specific user

5. **my_followers** (detail=False, GET)
   - List followers of the current authenticated user

6. **my_following** (detail=False, GET)
   - List users followed by the current authenticated user

### Additional Views

- **follow_user_view**: Simplified view function for following
- **unfollow_user_view**: Simplified view function for unfollowing

## Permissions

All follow-related endpoints require authentication. Users can only:
- Follow/unfollow any other user
- Cannot follow themselves
- Cannot unfollow if not already following

## Usage Examples

### Python Requests Example

```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Follow a user
follow_response = requests.post(
    f"{BASE_URL}/users/2/follow/",
    headers=headers
)
print(follow_response.json())

# Get user's followers
followers_response = requests.get(
    f"{BASE_URL}/users/2/followers/",
    headers=headers
)
print(followers_response.json())

# Get current user's following list
my_following = requests.get(
    f"{BASE_URL}/users/my_following/",
    headers=headers
)
print(my_following.json())
```

### JavaScript/fetch Example

```javascript
const token = "your_auth_token";
const baseUrl = "http://localhost:8000/api";

// Follow a user
fetch(`${baseUrl}/users/2/follow/`, {
    method: "POST",
    headers: {
        "Authorization": `Token ${token}`,
        "Content-Type": "application/json"
    }
})
.then(response => response.json())
.then(data => console.log(data));

// Get followers
fetch(`${baseUrl}/users/2/followers/`, {
    headers: {
        "Authorization": `Token ${token}`
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Testing

### Manual Testing Steps

1. **Register two users:**
   ```bash
   # Register User A
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"username": "userA", "email": "userA@example.com", "password": "pass123456", "password_confirm": "pass123456"}'

   # Register User B
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"username": "userB", "email": "userB@example.com", "password": "pass123456", "password_confirm": "pass123456"}'
   ```

2. **User A follows User B:**
   ```bash
   curl -X POST http://localhost:8000/api/users/2/follow/ \
     -H "Authorization: Token USER_A_TOKEN"
   ```

3. **User A views User B's followers:**
   ```bash
   curl -X GET http://localhost:8000/api/users/2/followers/ \
     -H "Authorization: Token USER_A_TOKEN"
   ```

4. **User A checks their following list:**
   ```bash
   curl -X GET http://localhost:8000/api/users/my_following/ \
     -H "Authorization: Token USER_A_TOKEN"
   ```

## Important Notes

- Follow relationships are **unidirectional**: A following B does not mean B follows A
- Users **cannot follow themselves**
- The `is_following` field in list responses indicates if the current user follows each displayed user
- All endpoints require authentication with a valid token
- Follow/unfollow actions are **atomic** and return immediate feedback

## Integration with Posts Feed

The follow relationships enable a dynamic feed feature where users can see posts only from users they follow. This will be implemented in a separate feature but relies on this follow infrastructure.

## Future Enhancements

1. **Block/Unblock Users**: Add ability for users to block other users
2. **Follow Requests**: Implement follow request approval system for private accounts
3. **Follow Notifications**: Notify users when they gain new followers
4. **Mutual Follows**: Display mutual follow indicator in user lists
5. **Follow Statistics**: Advanced analytics on follower growth trends
