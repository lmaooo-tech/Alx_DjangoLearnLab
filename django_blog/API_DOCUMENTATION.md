# Django Blog Authentication - API Documentation

## Overview
This document describes all authentication endpoints available in the Django Blog system, including request/response formats, authentication requirements, and examples.

---

## Base URL
```
http://localhost:8000
```

## Content-Type
All requests and responses use: `application/x-www-form-urlencoded` or `multipart/form-data` (for file uploads)

---

## Authentication Overview

### Session-Based Authentication
The system uses Django's session-based authentication:
- Username and password exchanged for session cookie
- Session cookie sent with each request
- Session destroyed on logout

### CSRF Protection
All POST requests require a CSRF token obtained from the form page.

---

## Endpoints

### 1. User Registration

#### Endpoint
```
POST /register/
```

#### Description
Create a new user account with email and optional name information.

#### Authentication Required
No (Public)

#### Request Format
```html
<form method="post" enctype="application/x-www-form-urlencoded">
    {% csrf_token %}
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="text" name="first_name">
    <input type="text" name="last_name">
    <input type="password" name="password1" required>
    <input type="password" name="password2" required>
</form>
```

#### Form Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Unique username (3-150 chars) |
| `email` | string | Yes | Valid, unique email address |
| `first_name` | string | No | User's first name (max 30 chars) |
| `last_name` | string | No | User's last name (max 150 chars) |
| `password1` | string | Yes | Password (min 8 chars) |
| `password2` | string | Yes | Password confirmation (must match password1) |
| `csrfmiddlewaretoken` | string | Yes | CSRF token (auto-included by {% csrf_token %}) |

#### Response

**Success (201/302):**
```
Redirect to /profile/
Set-Cookie: sessionid=<session_cookie>
```

**Validation Error (200):**
```html
<!-- Page re-rendered with form errors -->
<div class="form-errors">
    <p class="error">Username already exists</p>
</div>
```

#### Error Responses

| Error | Cause | Solution |
|-------|-------|----------|
| Username already exists | Username taken | Choose different username |
| Email address already registered | Email taken | Use different email or login |
| Passwords don't match | password1 ≠ password2 | Ensure passwords match |
| Password too short | Less than 8 characters | Use at least 8 characters |
| Password too common | Common password | Use more complex password |
| Invalid email format | Email doesn't match RFC 5322 | Enter valid email address |

#### Example Request (cURL)
```bash
curl -X POST http://localhost:8000/register/ \
  -d "username=john_doe" \
  -d "email=john@example.com" \
  -d "first_name=John" \
  -d "last_name=Doe" \
  -d "password1=SecurePass123!" \
  -d "password2=SecurePass123!" \
  -d "csrfmiddlewaretoken=<token>"
```

#### Example Response
```
HTTP/1.1 302 Found
Location: /profile/
Set-Cookie: sessionid=xyz123; Path=/; HttpOnly
```

---

### 2. User Login

#### Endpoint
```
POST /login/
GET /login/
```

#### Description
Authenticate user with username and password. Returns session cookie on success.

#### Authentication Required
No (Public)

#### Request Format
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="username" required>
    <input type="password" name="password" required>
</form>
```

#### Form Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Username or email |
| `password` | string | Yes | User's password |
| `csrfmiddlewaretoken` | string | Yes | CSRF token |

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `next` | string | URL to redirect after login |

#### Response

**Success (302):**
```
Redirect to /profile/ (or ?next parameter)
Set-Cookie: sessionid=<session_cookie>
```

**Failure (200):**
```html
<div class="messages">
    <div class="alert alert-error">
        Invalid username or password.
    </div>
</div>
<!-- Form re-rendered for retry -->
```

#### Error Responses

| Error | Cause |
|-------|-------|
| Invalid username or password | Wrong credentials |
| User account disabled | Account deactivated |

#### Example Request (cURL)
```bash
curl -X POST http://localhost:8000/login/ \
  -d "username=john_doe" \
  -d "password=SecurePass123!" \
  -d "csrfmiddlewaretoken=<token>"
```

#### Example Response
```
HTTP/1.1 302 Found
Location: /profile/
Set-Cookie: sessionid=abc456; Path=/; HttpOnly
```

---

### 3. User Logout

#### Endpoint
```
GET /logout/
POST /logout/
```

#### Description
End user session and clear session cookie.

#### Authentication Required
Yes (Logged in user)

#### Request Format
```html
<a href="{% url 'logout' %}">Logout</a>
```

#### Response

**Success (302):**
```
Redirect to /login/
Set-Cookie: sessionid=; Expires=<past_date>; Path=/
```

#### Example Request (cURL)
```bash
curl -X GET http://localhost:8000/logout/ \
  -H "Cookie: sessionid=xyz123"
```

#### Example Response
```
HTTP/1.1 302 Found
Location: /login/
Set-Cookie: sessionid=; Expires=Thu, 01-Jan-1970 00:00:01 GMT; Path=/
```

---

### 4. User Profile (View)

#### Endpoint
```
GET /profile/
```

#### Description
Retrieve and display authenticated user's profile information.

#### Authentication Required
Yes (Logged in user)

#### Response

**Success (200):**
```html
<div class="profile-header">
    <img src="/media/profile_pictures/john_123.jpg" alt="john_doe">
    <h3>John Doe</h3>
    <p class="username">@john_doe</p>
    <p>Member Since: February 14, 2026</p>
</div>
<div class="profile-info">
    <p>Bio: I'm a Django developer</p>
    <p>Location: San Francisco, CA</p>
</div>
```

**Not Authenticated (302):**
```
Redirect to /login/?next=/profile/
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | User's login name |
| `email` | string | User's email |
| `first_name` | string | First name |
| `last_name` | string | Last name |
| `date_joined` | datetime | Account creation date |
| `profile_picture` | URL | Profile image path |
| `bio` | string | User biography |
| `location` | string | User's location |
| `website` | URL | User's website |

#### Example Request (cURL)
```bash
curl -X GET http://localhost:8000/profile/ \
  -H "Cookie: sessionid=xyz123"
```

#### Example Response
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<html>
  <!-- Profile page HTML -->
</html>
```

---

### 5. Profile Update

#### Endpoint
```
POST /profile/
```

#### Description
Update authenticated user's profile information.

#### Authentication Required
Yes (Logged in user)

#### Request Format
```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="text" name="first_name">
    <input type="text" name="last_name">
    <input type="email" name="email" required>
    <textarea name="bio"></textarea>
    <input type="text" name="location">
    <input type="url" name="website">
    <input type="file" name="profile_picture">
</form>
```

#### Form Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `first_name` | string | No | User's first name |
| `last_name` | string | No | User's last name |
| `email` | string | Yes | Email (must be unique) |
| `bio` | string | No | Biography (max 500 chars) |
| `location` | string | No | Location/city |
| `website` | URL | No | Website URL |
| `profile_picture` | file | No | Image file (JPG, PNG) |
| `csrfmiddlewaretoken` | string | Yes | CSRF token |

#### Response

**Success (302):**
```
Redirect to /profile/
Message: "Your profile has been updated successfully."
```

**Validation Error (200):**
```html
<div class="form-errors">
    <p class="error">This email address is already in use.</p>
</div>
<!-- Form re-rendered with previous values -->
```

#### Error Responses

| Error | Cause | Solution |
|-------|-------|----------|
| Email already in use | Email associated with another account | Use unique email |
| Invalid URL format | Website URL malformed | Enter valid URL or leave blank |
| File too large | Image exceeds size limit | Upload smaller image |
| Invalid file type | Non-image file uploaded | Upload JPG or PNG |

#### Example Request (cURL with file)
```bash
curl -X POST http://localhost:8000/profile/ \
  -H "Cookie: sessionid=xyz123" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "email=john@example.com" \
  -F "bio=Django developer" \
  -F "location=San Francisco" \
  -F "website=https://example.com" \
  -F "profile_picture=@profile.jpg" \
  -F "csrfmiddlewaretoken=<token>"
```

#### Example Response
```
HTTP/1.1 302 Found
Location: /profile/
```

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful, page rendered |
| 302 | Found | Redirect response |
| 400 | Bad Request | Invalid form data |
| 403 | Forbidden | CSRF token missing/invalid |
| 404 | Not Found | URL doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method (GET vs POST) |
| 500 | Server Error | Internal server error |

---

## Authentication Cookie Format

```
Set-Cookie: sessionid=<hex_string>; Path=/; HttpOnly; Secure; SameSite=Lax
```

### Cookie Attributes
- **Path=/**: Valid for entire domain
- **HttpOnly**: Not accessible via JavaScript (security)
- **Secure**: Only sent over HTTPS (production)
- **SameSite=Lax**: CSRF protection

---

## Flow Diagrams

### Registration Flow
```
User Request
    ↓
GET /register/
    ↓
Display Form with CSRF Token
    ↓
User Fills Form
    ↓
POST /register/
    ↓
Validate Form ──→ Invalid? → Show Errors (200)
    ↓
Valid
    ↓
Create User
    ↓
Auto Create UserProfile
    ↓
Auto Login (Create Session)
    ↓
Redirect to /profile/ (302)
    ↓
Set Session Cookie
    ↓
Display Profile Page
```

### Login Flow
```
User Request
    ↓
GET /login/?next=/protected/
    ↓
Display Form with CSRF Token
    ↓
User Enters Credentials
    ↓
POST /login/
    ↓
Authenticate User ──→ Failed? → Show Error (200)
    ↓
Success
    ↓
Create Session
    ↓
Redirect to ?next param (302)
    ↓
Set Session Cookie
    ↓
Display Requested Page
```

### Protected Page Access
```
User Request
    ↓
GET /profile/
    ↓
Check Session Cookie
    ↓
Valid? ──→ No → Redirect to /login/?next=/profile/ (302)
    ↓
Valid
    ↓
Load User Profile
    ↓
Render Profile Page (200)
```

---

## Common Integration Examples

### Using with JavaScript Fetch API
```javascript
// Get CSRF token from page
const token = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Make login request
fetch('/login/', {
    method: 'POST',
    credentials: 'include',  // Include cookies
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': token,
    },
    body: new URLSearchParams({
        'username': 'john_doe',
        'password': 'SecurePass123!'
    })
})
.then(response => {
    if (response.ok) {
        window.location.href = '/profile/';
    } else {
        console.error('Login failed');
    }
});
```

### Using with Python Requests
```python
import requests

session = requests.Session()

# Get CSRF token
response = session.get('http://localhost:8000/login/')
csrf_token = response.cookies['csrftoken']

# Login
login_data = {
    'username': 'john_doe',
    'password': 'SecurePass123!',
    'csrfmiddlewaretoken': csrf_token
}
response = session.post('http://localhost:8000/login/', data=login_data)
print(response.status_code)  # 302 on success
```

### Using with jQuery
```javascript
// Get CSRF token
var csrftoken = $('[name=csrfmiddlewaretoken]').val();

$.ajax({
    url: '/profile/',
    type: 'POST',
    data: {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        csrfmiddlewaretoken: csrftoken
    },
    success: function() {
        console.log('Profile updated');
        window.location.reload();
    }
});
```

---

## Testing Endpoints

### Using Postman

1. **Registration**
   - URL: `POST http://localhost:8000/register/`
   - Body: form-data with all fields
   - Note: CSRF token required (get from GET /register/)

2. **Login**
   - URL: `POST http://localhost:8000/login/`
   - Body: form-data with username, password
   - Cookie: session auto-managed

3. **Profile**
   - URL: `GET http://localhost:8000/profile/`
   - Headers: Cookie from login
   - Or: `POST` to update profile

### Using cURL

```bash
# Get CSRF token
curl http://localhost:8000/register/ \
  -c cookies.txt

# Register
curl -X POST http://localhost:8000/register/ \
  -b cookies.txt \
  -c cookies.txt \
  -d "username=testuser" \
  -d "email=test@example.com" \
  -d "password1=Test123!@" \
  -d "password2=Test123!@"

# View profile
curl http://localhost:8000/profile/ \
  -b cookies.txt
```

---

## Rate Limiting (Future)

When implemented, rate limiting will apply to:
- Login: 5 attempts per minute per IP
- Registration: 3 attempts per hour per IP
- Profile updates: 10 per hour per user

Response on limit exceeded:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

---

## Performance Considerations

### Response Times (Target)
- Registration: < 500ms
- Login: < 300ms
- Profile load: < 200ms
- Profile update: < 500ms

### Database Queries
- Login: 1-2 queries
- Profile view: 2 queries (User + UserProfile)
- Profile update: 2-3 queries

---

## Security Headers

All responses include:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: same-origin
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial release |

---

## Support

For issues or questions:
- Review [AUTH_README.md](AUTH_README.md)
- Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- See [TESTING.md](TESTING.md) for test examples
- Review [SECURITY.md](SECURITY.md) for security details

---

**Last Updated**: February 2026
**Django Version**: 6.0+
**Status**: Production Ready
