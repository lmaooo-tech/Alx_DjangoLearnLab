# User Authentication Testing Guide

This document provides comprehensive testing procedures for the user authentication features in the relationship_app.

## Authentication Features Implemented

### 1. **User Registration** (`/relationship_app/register/`)
- **Functionality**: Allows new users to create accounts
- **Fields**: Username, Email, Password, Password Confirmation
- **Validation**:
  - All fields are required
  - Passwords must match
  - Username must be unique
  - Email must be unique

### 2. **User Login** (`/relationship_app/login/`)
- **Functionality**: Authenticates users and creates sessions
- **Fields**: Username, Password
- **Features**:
  - Redirects already authenticated users to books list
  - Validates credentials against database
  - Creates secure session upon successful login

### 3. **User Logout** (`/relationship_app/logout/`)
- **Functionality**: Terminates user session
- **Features**:
  - Clears session data
  - Displays logout confirmation
  - Redirects to books list

## Testing Procedures

### Test Case 1: User Registration

**Steps:**
1. Navigate to `http://localhost:8000/relationship_app/register/`
2. Fill in the registration form:
   - Username: `testuser1`
   - Email: `testuser1@example.com`
   - Password: `SecurePassword123`
   - Confirm Password: `SecurePassword123`
3. Click "Create Account" button

**Expected Results:**
- Success message: "Registration successful! Please log in."
- Redirected to login page
- User is saved in database

**Test Case 1b: Duplicate Username**
1. Try to register with username: `testuser1` (same as Test Case 1)
2. Fill in other fields with new data

**Expected Results:**
- Error message: "Username already exists."
- Remain on registration page

**Test Case 1c: Duplicate Email**
1. Try to register with email: `testuser1@example.com` (same as Test Case 1)
2. Fill in other fields with new data

**Expected Results:**
- Error message: "Email already registered."
- Remain on registration page

**Test Case 1d: Password Mismatch**
1. Fill in the registration form with mismatched passwords
2. Password: `SecurePassword123`
3. Confirm Password: `DifferentPassword456`

**Expected Results:**
- Error message: "Passwords do not match."
- Remain on registration page

---

### Test Case 2: User Login

**Steps:**
1. Navigate to `http://localhost:8000/relationship_app/login/`
2. Fill in the login form:
   - Username: `testuser1`
   - Password: `SecurePassword123`
3. Click "Login" button

**Expected Results:**
- Success message: "Welcome back, testuser1!"
- Redirected to books list page
- Session is created
- User remains logged in

**Test Case 2b: Invalid Credentials**
1. Navigate to login page
2. Fill in the login form:
   - Username: `testuser1`
   - Password: `WrongPassword`
3. Click "Login" button

**Expected Results:**
- Error message: "Invalid username or password."
- Remain on login page
- No session is created

**Test Case 2c: Already Authenticated**
1. Login with valid credentials (Test Case 2)
2. Navigate to `http://localhost:8000/relationship_app/login/`

**Expected Results:**
- Redirected to books list page (if already logged in)
- No login form displayed

---

### Test Case 3: User Logout

**Steps:**
1. Login successfully (Test Case 2)
2. Navigate to `http://localhost:8000/relationship_app/logout/`

**Expected Results:**
- Success message: "Goodbye, [username]! You have been logged out."
- Session is cleared
- Redirected to books list page
- User can no longer access protected content without re-logging in

---

## Running Tests in Django Shell

### Create Test User

```bash
# Start Django shell
python manage.py shell

# Import User model
from django.contrib.auth.models import User

# Create a test user
user = User.objects.create_user(
    username='shelluser',
    email='shelluser@example.com',
    password='TestPassword123'
)

# Verify user was created
print(user.username, user.email)
```

### Verify User Authentication

```bash
# In Django shell
from django.contrib.auth import authenticate

# Test correct credentials
user = authenticate(username='shelluser', password='TestPassword123')
print(user)  # Should print the user object

# Test incorrect credentials
user = authenticate(username='shelluser', password='WrongPassword')
print(user)  # Should print None
```

### List All Users

```bash
# In Django shell
from django.contrib.auth.models import User

# Get all users
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}")
```

---

## Database Verification

After completing tests, verify data in database:

```bash
python manage.py shell

from django.contrib.auth.models import User

# Count registered users
print(f"Total users: {User.objects.count()}")

# Check specific user
user = User.objects.get(username='testuser1')
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Last Login: {user.last_login}")
print(f"Date Joined: {user.date_joined}")
```

---

## Session Verification

Check Django sessions:

```bash
# In Django shell
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

# List active sessions
sessions = Session.objects.filter(expire_date__gte=timezone.now())
print(f"Active sessions: {sessions.count()}")

# View session data (if needed)
for session in sessions:
    data = session.get_decoded()
    print(data)
```

---

## URL Patterns Summary

| URL Path | View | Purpose |
|----------|------|---------|
| `/relationship_app/register/` | `register_view` | User account creation |
| `/relationship_app/login/` | `login_view` | User authentication |
| `/relationship_app/logout/` | `logout_view` | Session termination |
| `/relationship_app/books/` | `list_all_books` | Display all books |
| `/relationship_app/library/<int:pk>/` | `LibraryDetailView` | Library details |

---

## Security Features

✓ CSRF Protection ({% csrf_token %} in forms)
✓ Password Hashing (Django's default PBKDF2)
✓ Session Management (secure cookies)
✓ Input Validation (server-side)
✓ User Model Integration (Django built-in)

---

## Troubleshooting

**Issue**: "Page not found" error
- **Solution**: Ensure URLs are properly configured in `relationship_app/urls.py`

**Issue**: CSRF verification failed
- **Solution**: Ensure `{% csrf_token %}` is included in all POST forms

**Issue**: Messages not displaying
- **Solution**: Verify `django.contrib.messages` is in INSTALLED_APPS

**Issue**: Database errors
- **Solution**: Run `python manage.py migrate` to ensure database is up to date

---

## Next Steps

- Add email verification for registration
- Implement password reset functionality
- Add user profile management
- Implement permission-based access control
- Add two-factor authentication
