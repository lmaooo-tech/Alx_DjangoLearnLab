# Social Media API - Complete Endpoint Reference

## Base Information

- **Base URL:** `http://localhost:8000/api`
- **Authentication:** Token-based (HTTP Bearer Token)
- **Default Port:** 8000
- **Media Storage:** Local filesystem (development)

---

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [User Management Endpoints](#user-management-endpoints)
3. [Follow Management Endpoints](#follow-management-endpoints)
4. [Post Management Endpoints](#post-management-endpoints)
5. [Feed Endpoints](#feed-endpoints)
6. [Comment Endpoints](#comment-endpoints)
7. [Like Endpoints](#like-endpoints)
8. [Error Responses](#error-responses)

---

## Authentication Endpoints

### Register User

**Endpoint:** `POST /auth/register/`

**Authentication:** Not required

**Description:** Create a new user account

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": null,
        "profile_picture": null,
        "followers_count": 0,
        "following_count": 0,
        "created_at": "2026-02-21T12:00:00Z",
        "updated_at": "2026-02-21T12:00:00Z"
    },
    "token": "abc123def456ghi789..."
}
```

**Status Codes:**
- `201 Created` - User registered successfully
- `400 Bad Request` - Invalid data or username already exists

---

### Login User

**Endpoint:** `POST /auth/login/`

**Authentication:** Not required

**Description:** Authenticate user and get authentication token

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": null,
        "profile_picture": null,
        "followers_count": 0,
        "following_count": 0,
        "created_at": "2026-02-21T12:00:00Z",
        "updated_at": "2026-02-21T12:00:00Z"
    },
    "token": "abc123def456ghi789..."
}
```

**Status Codes:**
- `200 OK` - Login successful
- `400 Bad Request` - Invalid credentials

---

### Get Current User Profile

**Endpoint:** `GET /auth/profile/`

**Authentication:** Required (Token)

**Description:** Get authenticated user's profile information

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Software developer and tech enthusiast",
    "profile_picture": null,
    "followers_count": 5,
    "following_count": 10,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token

---

### Update Current User Profile

**Endpoint:** `PATCH /auth/profile/`

**Authentication:** Required (Token)

**Description:** Update authenticated user's profile information

**Request Body (all fields optional):**
```json
{
  "first_name": "Jonathan",
  "last_name": "Doe",
  "bio": "Updated bio text",
  "profile_picture": "<image_file>"
}
```

**cURL Example:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jonathan",
    "bio": "Updated bio text"
  }'
```

**Response (200 OK):**
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "Jonathan",
        "last_name": "Doe",
        "bio": "Updated bio text",
        "profile_picture": null,
        "followers_count": 5,
        "following_count": 10,
        "created_at": "2026-02-21T12:00:00Z",
        "updated_at": "2026-02-21T12:00:00Z"
    }
}
```

**Status Codes:**
- `200 OK` - Profile updated
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Invalid or missing token

---

## User Management Endpoints

### List All Users

**Endpoint:** `GET /users/`

**Authentication:** Not required

**Description:** Get list of all users with pagination

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/users/?page=1&page_size=10"
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
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "bio": null,
            "profile_picture": null,
            "followers_count": 0,
            "following_count": 0,
            "created_at": "2026-02-21T12:00:00Z",
            "updated_at": "2026-02-21T12:00:00Z"
        },
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": null,
            "profile_picture": null,
            "followers_count": 1,
            "following_count": 2,
            "created_at": "2026-02-21T13:00:00Z",
            "updated_at": "2026-02-21T13:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success

---

### Get User Profile by ID

**Endpoint:** `GET /users/{user_id}/`

**Authentication:** Not required

**Description:** Get specific user's profile information

**Path Parameters:**
- `user_id` - The ID of the user

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/users/1/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Software developer",
    "profile_picture": null,
    "followers_count": 5,
    "following_count": 10,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - User not found

---

## Follow Management Endpoints

### Follow a User

**Endpoint:** `POST /auth/follow/{user_id}/`

**Authentication:** Required (Token)

**Description:** Follow another user

**Path Parameters:**
- `user_id` - The ID of the user to follow

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/follow/2/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK):**
```json
{
    "message": "You are now following jane_smith",
    "status": "following",
    "user": {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com"
    },
    "followers_count": 2,
    "following_count": 1
}
```

**Status Codes:**
- `200 OK` - Successfully followed
- `400 Bad Request` - Already following or trying to follow self
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User to follow not found

---

### Unfollow a User

**Endpoint:** `POST /auth/unfollow/{user_id}/`

**Authentication:** Required (Token)

**Description:** Unfollow another user

**Path Parameters:**
- `user_id` - The ID of the user to unfollow

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/unfollow/2/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK):**
```json
{
    "message": "You have unfollowed jane_smith",
    "status": "not_following",
    "user": {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com"
    },
    "followers_count": 1,
    "following_count": 0
}
```

**Status Codes:**
- `200 OK` - Successfully unfollowed
- `400 Bad Request` - Not following this user
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User to unfollow not found

---

### Get User's Followers

**Endpoint:** `GET /users/{user_id}/followers/`

**Authentication:** Not required

**Description:** Get list of users following a specific user

**Path Parameters:**
- `user_id` - The ID of the user

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/users/1/followers/
```

**Response (200 OK):**
```json
{
    "count": 2,
    "user": "john_doe",
    "followers": [
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": null,
            "profile_picture": null,
            "is_following": false
        },
        {
            "id": 3,
            "username": "bob_johnson",
            "email": "bob@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "bio": null,
            "profile_picture": null,
            "is_following": false
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - User not found

---

### Get User's Following List

**Endpoint:** `GET /users/{user_id}/following/`

**Authentication:** Not required

**Description:** Get list of users that a specific user is following

**Path Parameters:**
- `user_id` - The ID of the user

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/users/1/following/
```

**Response (200 OK):**
```json
{
    "count": 3,
    "user": "john_doe",
    "following": [
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": null,
            "profile_picture": null,
            "is_following": true
        },
        {
            "id": 3,
            "username": "bob_johnson",
            "email": "bob@example.com",
            "first_name": "Bob",
            "last_name": "Johnson",
            "bio": null,
            "profile_picture": null,
            "is_following": true
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - User not found

---

### Get Current User's Followers

**Endpoint:** `GET /auth/my_followers/`

**Authentication:** Required (Token)

**Description:** Get list of users following the authenticated user

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/auth/my_followers/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (200 OK):**
```json
{
    "count": 2,
    "followers": [
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": null,
            "profile_picture": null,
            "is_following": false
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token

---

### Get Current User's Following List

**Endpoint:** `GET /auth/my_following/`

**Authentication:** Required (Token)

**Description:** Get list of users the authenticated user is following

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/auth/my_following/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (200 OK):**
```json
{
    "count": 3,
    "following": [
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": null,
            "profile_picture": null,
            "is_following": true
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token

---

## Post Management Endpoints

### Create a Post

**Endpoint:** `POST /posts/`

**Authentication:** Required (Token)

**Description:** Create a new post

**Request Body:**
```json
{
  "content": "This is my first post!",
  "image": "<optional_image_file>"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my first post!"
  }'
```

**Response (201 Created):**
```json
{
    "id": 1,
    "author": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": null,
        "profile_picture": null,
        "is_following": false
    },
    "content": "This is my first post!",
    "image": null,
    "likes": [],
    "likes_count": 0,
    "is_liked_by_user": false,
    "comments": [],
    "comments_count": 0,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:00:00Z"
}
```

**Status Codes:**
- `201 Created` - Post created successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Invalid or missing token

---

### List All Posts

**Endpoint:** `GET /posts/`

**Authentication:** Not required

**Description:** Get list of all posts with pagination

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)
- `ordering` - Order by field (default: -created_at)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/?page=1&page_size=10&ordering=-created_at"
```

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "author": {
                "id": 2,
                "username": "jane_smith",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Latest post from Jane",
            "image": null,
            "likes_count": 3,
            "is_liked_by_user": false,
            "comments_count": 2,
            "created_at": "2026-02-21T15:00:00Z",
            "updated_at": "2026-02-21T15:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success

---

### Get Post by ID

**Endpoint:** `GET /posts/{post_id}/`

**Authentication:** Not required

**Description:** Get specific post with all details (likes and comments)

**Path Parameters:**
- `post_id` - The ID of the post

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/posts/1/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "author": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": null,
        "profile_picture": null,
        "is_following": false
    },
    "content": "This is my first post!",
    "image": null,
    "likes": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "username": "jane_smith",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "created_at": "2026-02-21T12:05:00Z"
        }
    ],
    "likes_count": 1,
    "is_liked_by_user": false,
    "comments": [
        {
            "id": 1,
            "author": {
                "id": 2,
                "username": "jane_smith",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Great post!",
            "created_at": "2026-02-21T12:10:00Z",
            "updated_at": "2026-02-21T12:10:00Z"
        }
    ],
    "comments_count": 1,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Post not found

---

### Update a Post

**Endpoint:** `PUT /posts/{post_id}/`

**Authentication:** Required (Token)

**Description:** Update a post (only by author)

**Path Parameters:**
- `post_id` - The ID of the post to update

**Request Body:**
```json
{
  "content": "Updated post content"
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/api/posts/1/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated post content"
  }'
```

**Response (200 OK):**
```json
{
    "id": 1,
    "author": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": null,
        "profile_picture": null,
        "is_following": false
    },
    "content": "Updated post content",
    "image": null,
    "likes_count": 1,
    "is_liked_by_user": false,
    "comments_count": 1,
    "created_at": "2026-02-21T12:00:00Z",
    "updated_at": "2026-02-21T12:15:00Z"
}
```

**Status Codes:**
- `200 OK` - Post updated
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not the post author
- `404 Not Found` - Post not found

---

### Delete a Post

**Endpoint:** `DELETE /posts/{post_id}/`

**Authentication:** Required (Token)

**Description:** Delete a post (only by author)

**Path Parameters:**
- `post_id` - The ID of the post to delete

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/posts/1/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (204 No Content)**
```
(Empty response body)
```

**Status Codes:**
- `204 No Content` - Post deleted successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Not the post author
- `404 Not Found` - Post not found

---

### Get Posts by User

**Endpoint:** `GET /posts/user_posts/`

**Authentication:** Not required

**Description:** Get all posts by a specific user (query parameter based)

**Query Parameters:**
- `username` - Username of the user

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/user_posts/?username=john_doe"
```

**Response (200 OK):**
```json
{
    "count": 3,
    "username": "john_doe",
    "posts": [
        {
            "id": 5,
            "author": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Latest post",
            "image": null,
            "likes_count": 2,
            "is_liked_by_user": false,
            "comments_count": 1,
            "created_at": "2026-02-21T15:00:00Z",
            "updated_at": "2026-02-21T15:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - User not found

---

## Feed Endpoints

### Get Personalized Feed

**Endpoint:** `GET /feed/`

**Authentication:** Required (Token)

**Description:** Get feed with posts from all users the authenticated user is following

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `ordering` - Order by field (default: -created_at)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/feed/?page=1&page_size=20" \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (200 OK):**
```json
{
    "count": 5,
    "posts": [
        {
            "id": 10,
            "author": {
                "id": 2,
                "username": "jane_smith",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "bio": null,
                "profile_picture": null,
                "is_following": true
            },
            "content": "Just had an amazing coffee!",
            "image": null,
            "likes_count": 5,
            "is_liked_by_user": true,
            "comments_count": 2,
            "created_at": "2026-02-21T15:00:00Z",
            "updated_at": "2026-02-21T15:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token

---

### Get User-Specific Feed

**Endpoint:** `GET /feed/{username}/`

**Authentication:** Not required

**Description:** Get all posts from a specific user

**Path Parameters:**
- `username` - The username of the user

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/feed/john_doe/
```

**Response (200 OK):**
```json
{
    "count": 3,
    "username": "john_doe",
    "posts": [
        {
            "id": 5,
            "author": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "This is my latest post",
            "image": null,
            "likes_count": 3,
            "is_liked_by_user": false,
            "comments_count": 1,
            "created_at": "2026-02-21T15:00:00Z",
            "updated_at": "2026-02-21T15:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - User not found

---

### Explore Recent Posts

**Endpoint:** `GET /explore/`

**Authentication:** Not required

**Description:** Get recent posts from all users (up to 50 posts)

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/explore/?page=1&page_size=20"
```

**Response (200 OK):**
```json
{
    "count": 12,
    "posts": [
        {
            "id": 15,
            "author": {
                "id": 3,
                "username": "bob_johnson",
                "email": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Johnson",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Check out this amazing discovery!",
            "image": null,
            "likes_count": 12,
            "is_liked_by_user": false,
            "comments_count": 5,
            "created_at": "2026-02-21T20:00:00Z",
            "updated_at": "2026-02-21T20:00:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success

---

## Comment Endpoints

### Add Comment to Post

**Endpoint:** `POST /posts/{post_id}/comment/`

**Authentication:** Required (Token)

**Description:** Add a comment to a post

**Path Parameters:**
- `post_id` - The ID of the post

**Request Body:**
```json
{
  "content": "Great post! I really enjoyed it."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/posts/1/comment/ \
  -H "Authorization: Token abc123def456ghi789..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post! I really enjoyed it."
  }'
```

**Response (201 Created):**
```json
{
    "id": 1,
    "author": {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "bio": null,
        "profile_picture": null,
        "is_following": false
    },
    "content": "Great post! I really enjoyed it.",
    "created_at": "2026-02-21T12:10:00Z",
    "updated_at": "2026-02-21T12:10:00Z"
}
```

**Status Codes:**
- `201 Created` - Comment added successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Post not found

---

### Get Post Comments

**Endpoint:** `GET /posts/{post_id}/comments/`

**Authentication:** Not required

**Description:** Get all comments for a post

**Path Parameters:**
- `post_id` - The ID of the post

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/1/comments/?page=1&page_size=10"
```

**Response (200 OK):**
```json
{
    "count": 2,
    "comments": [
        {
            "id": 1,
            "author": {
                "id": 2,
                "username": "jane_smith",
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Great post! I really enjoyed it.",
            "created_at": "2026-02-21T12:10:00Z",
            "updated_at": "2026-02-21T12:10:00Z"
        },
        {
            "id": 2,
            "author": {
                "id": 3,
                "username": "bob_johnson",
                "email": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Johnson",
                "bio": null,
                "profile_picture": null,
                "is_following": false
            },
            "content": "Totally agree with this!",
            "created_at": "2026-02-21T12:15:00Z",
            "updated_at": "2026-02-21T12:15:00Z"
        }
    ]
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Post not found

---

## Like Endpoints

### Like a Post

**Endpoint:** `POST /posts/{post_id}/like/`

**Authentication:** Required (Token)

**Description:** Like a post

**Path Parameters:**
- `post_id` - The ID of the post to like

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/posts/1/like/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (201 Created):**
```json
{
    "message": "Post liked successfully",
    "likes_count": 5
}
```

**Status Codes:**
- `201 Created` - Post liked successfully
- `400 Bad Request` - Already liked or other error
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Post not found

---

### Unlike a Post

**Endpoint:** `POST /posts/{post_id}/unlike/`

**Authentication:** Required (Token)

**Description:** Unlike a post

**Path Parameters:**
- `post_id` - The ID of the post to unlike

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/posts/1/unlike/ \
  -H "Authorization: Token abc123def456ghi789..."
```

**Response (200 OK):**
```json
{
    "message": "Post unliked successfully",
    "likes_count": 4
}
```

**Status Codes:**
- `200 OK` - Post unliked successfully
- `400 Bad Request` - Not liked by this user
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Post not found

---

## Error Responses

### 400 Bad Request

Returned when the request contains invalid data.

**Example:**
```json
{
    "field_name": [
        "This field is required.",
        "Ensure this value has at most 500 characters."
    ]
}
```

---

### 401 Unauthorized

Returned when authentication is required but not provided or invalid.

**Example:**
```json
{
    "detail": "Invalid token."
}
```

---

### 403 Forbidden

Returned when user lacks permission to perform the action.

**Example:**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 404 Not Found

Returned when the requested resource doesn't exist.

**Example:**
```json
{
    "detail": "Not found."
}
```

---

### 500 Internal Server Error

Returned when an unexpected server error occurs.

**Example:**
```json
{
    "detail": "Internal server error."
}
```

---

## Common cURL Patterns

### Save Token to Variable
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepassword123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"
```

### Use Token in Request
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token $TOKEN"
```

### Formatted JSON Output
```bash
curl -X GET http://localhost:8000/api/posts/ | jq '.'
```

### Save to File
```bash
curl -X GET http://localhost:8000/api/posts/ > posts.json
```

### Include Response Headers
```bash
curl -i http://localhost:8000/api/posts/
```

### Check Status Code Only
```bash
curl -o /dev/null -s -w "%{http_code}\n" http://localhost:8000/api/posts/
```

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users
- Implement using Django REST Framework's throttling classes

---

## Pagination

All list endpoints support pagination with:

- `page`: Page number (1-indexed)
- `page_size`: Number of items per page (default: 10-20)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/posts/?page=2&page_size=5"
```

**Response includes:**
- `count`: Total number of items
- `next`: URL to next page (or null)
- `previous`: URL to previous page (or null)
- `results`: Array of items

---

## Filtering & Ordering

### Ordering
Most list endpoints support ordering:

```bash
curl -X GET "http://localhost:8000/api/posts/?ordering=-created_at"
```

Available ordering fields:
- `created_at` - Creation date
- `-created_at` - Creation date (descending)
- `username` - Username
- `likes_count` - Number of likes

### Searching
Some endpoints support search:

```bash
curl -X GET "http://localhost:8000/api/auth/search/?q=john"
```

---

## Best Practices

### Security
1. Always use HTTPS in production
2. Never expose tokens in URLs
3. Use short token expiration times
4. Rotate tokens regularly
5. Validate all user input

### Performance
1. Use pagination for list endpoints
2. Implement caching for frequently accessed data
3. Use select_related() and prefetch_related() to optimize queries
4. Consider implementing rate limiting

### Error Handling
1. Always check response status code
2. Parse error messages for debugging
3. Implement retry logic for transient errors
4. Log all API failures

### Testing
1. Test with both valid and invalid data
2. Test edge cases (empty feeds, no followers, etc.)
3. Test error responses
4. Test authentication and permissions
5. Test pagination and filtering

---

## Example Workflows

### Complete User Journey

```bash
# 1. Register
REGISTER=$(curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }')

TOKEN=$(echo $REGISTER | jq -r '.token')
USER_ID=$(echo $REGISTER | jq -r '.user.id')

# 2. Follow other users
curl -s -X POST http://localhost:8000/api/auth/follow/2/ \
  -H "Authorization: Token $TOKEN" | jq '.'

# 3. Create a post
POST=$(curl -s -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello world!"}')

POST_ID=$(echo $POST | jq -r '.id')

# 4. View feed
curl -s -X GET http://localhost:8000/api/feed/ \
  -H "Authorization: Token $TOKEN" | jq '.'

# 5. Like a post
curl -s -X POST http://localhost:8000/api/posts/$POST_ID/like/ \
  -H "Authorization: Token $TOKEN" | jq '.'
```

---

## Support & Documentation

For additional help:
- Check Django REST Framework documentation
- Review model definitions in `models.py`
- Check serializer definitions in `serializers.py`
- Review view implementations in `views.py`
