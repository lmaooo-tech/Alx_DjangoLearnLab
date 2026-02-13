# Django Blog Authentication Security Documentation

## Overview
This document outlines the security features implemented in the Django Blog authentication system, including password handling, CSRF protection, and best practices for secure user management.

---

## 1. Password Security

### 1.1 Hashing Algorithm
- **Algorithm**: PBKDF2 (Password-Based Key Derivation Function 2) with SHA256
- **Default Hasher**: `django.contrib.auth.hashers.PBKDF2PasswordHasher`
- **Iterations**: 600,000+ iterations (Django default)
- **Implementation**: Django's built-in `User.set_password()` method automatically hashes passwords

### 1.2 Password Storage
- Passwords are **never stored in plaintext**
- All passwords are hashed using Django's password hashing system
- Users cannot reset passwords to existing plaintext passwords
- Django enforces this automatically at the model level

### 1.3 Password Validation
Built-in Django password validators enforce:
- **UserAttributeSimilarityValidator**: Prevents passwords similar to user attributes
- **MinimumLengthValidator**: Minimum 8 characters required
- **CommonPasswordValidator**: Rejects common passwords from 20,000+ common password list
- **NumericPasswordValidator**: Rejects purely numeric passwords

### 1.4 Password Verification
- Passwords are verified using Django's `authenticate()` function
- Timing-attack resistant comparison using `django.contrib.auth.hashers.check_password()`
- Login attempts with wrong passwords do not reveal whether username exists

---

## 2. CSRF Protection

### 2.1 CSRF Token Implementation
All forms include CSRF tokens using Django's `{% csrf_token %}` template tag:

**Login Form** (`login.html`):
```html
<form method="post" class="auth-form">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**Registration Form** (`register.html`):
```html
<form method="post" class="auth-form">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**Profile Form** (`profile.html`):
```html
<form method="post" enctype="multipart/form-data" class="profile-form">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 2.2 CSRF Middleware
- **Enabled**: `django.middleware.csrf.CsrfViewMiddleware` in settings
- **Token Validation**: Automatic validation on all POST requests
- **Protection Level**: Double-submit cookie pattern

### 2.3 CSRF Token Configuration
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # Protects against CSRF
    # ... other middleware
]

CSRF_COOKIE_SECURE = True      # Only send cookie over HTTPS (production)
CSRF_COOKIE_HTTPONLY = False   # Token must be readable by JS for forms
CSRF_TRUSTED_ORIGINS = [...]   # Whitelist trusted origins
```

---

## 3. Authentication Security

### 3.1 Login Security (`login_view`)
- **Method**: Django's built-in `authenticate()` and `login()` functions
- **Session Management**: Django's session framework with signed cookies
- **Error Messages**: Generic "Invalid username or password" to prevent user enumeration
- **Timing Attacks**: Protected by Django's constant-time comparison

### 3.2 Logout Security (`logout_view`)
- **Session Cleanup**: Django's `logout()` function flushes session data
- **Cookie Deletion**: Session cookie is deleted from browser
- **Redirect**: User redirected to login page after logout
- **Next Page Handling**: Prevents open redirect vulnerabilities

### 3.3 Login Required Decorator
```python
@login_required(login_url='login')
def profile(request):
    # User must be authenticated to access
    pass
```

---

## 4. User Input Validation

### 4.1 Email Validation
- **Uniqueness Check**: Ensures no duplicate emails in database
- **Format Validation**: Django's `EmailField` validates RFC 5322 format
- **Case Handling**: Email comparison is case-insensitive

### 4.2 Form Validation
- **CustomUserCreationForm**:
  - Extended Django's built-in `UserCreationForm`
  - Validates all fields before database insertion
  - Email uniqueness validation with helpful error messages

- **UserProfileForm**:
  - Validates profile fields against model constraints
  - Email uniqueness check (excluding current user)
  - URL field validation for website input
  - File upload validation for profile pictures

### 4.3 Clean Methods
```python
def clean_email(self):
    """Validate that email is unique"""
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError('This email address is already registered.')
    return email
```

---

## 5. Session Security

### 5.1 Session Configuration
```python
# settings.py
SESSION_COOKIE_AGE = 1209600  # 2 weeks (adjust as needed)
SESSION_COOKIE_SECURE = True  # HTTPS only (production)
SESSION_COOKIE_HTTPONLY = True  # Not accessible via JavaScript
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Session persists
SESSION_SAVE_EVERY_REQUEST = False  # Improves performance
```

### 5.2 Session Invalidation
- Sessions are invalidated on logout via `django.contrib.auth.logout()`
- Sessions contain signed data, cannot be tampered with
- SessionKey is unique per user per login

---

## 6. Data Protection

### 6.1 Profile Picture Handling
- **Storage**: Uploaded to `media/profile_pictures/` directory
- **Security**: Files are stored outside web root in production
- **Validation**: Only image files accepted (configured in form)
- **Access Control**: Requires authentication to view user profile

### 6.2 Personal Data Protection
- **Email Verification**: Users can verify email ownership during registration
- **Email Uniqueness**: Prevents unauthorized account takeover
- **Profile Privacy**: Profile information only visible to authenticated users

---

## 7. Best Practices for Production

### 7.1 HTTPS Enforcement
```python
# settings.py (Production)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 7.2 Security Headers
```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filtering
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", 'data:', 'https:'),
}
```

### 7.3 Database Security
- Ensure database credentials are not in version control
- Use environment variables for sensitive configuration
- Use strong database passwords
- Limit database access to application server

### 7.4 Credential Management
```python
# .env file (NOT committed to git)
SECRET_KEY = 'your-secret-key-here'
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
DATABASE_URL = 'postgresql://user:password@host:5432/dbname'
```

---

## 8. Common Security Threats Mitigated

| Threat | Mitigation |
|--------|-----------|
| SQL Injection | Django ORM with parameterized queries |
| CSRF | CSRF tokens in all forms, middleware validation |
| XSS | Django template auto-escaping, output encoding |
| Brute Force | Implement rate limiting (external package) |
| Session Hijacking | Secure, HTTP-only session cookies |
| Password Weak | Django password validators enforced |
| Directory Traversal | Django's URL routing prevents direct file access |
| Open Redirect | Explicit redirect URLs using `reverse()` |

---

## 9. Testing Security

### 9.1 Running Tests
```bash
# Run all authentication tests
python manage.py test blog.tests

# Run specific test class
python manage.py test blog.tests.UserRegistrationTests

# Verbose output
python manage.py test blog.tests -v 2

# With coverage
coverage run --source='.' manage.py test blog.tests
coverage report
```

### 9.2 Test Coverage
The test suite includes:
- **Registration Tests**: Valid/invalid data, duplicate prevention, CSRF validation
- **Login Tests**: Valid/invalid credentials, CSRF validation, password visibility
- **Logout Tests**: Session cleanup, redirect verification
- **Profile Tests**: Authentication required, data updates, CSRF validation
- **Password Security Tests**: Hashing verification, validation enforcement

---

## 10. Security Checklist

- [x] All passwords are hashed using PBKDF2 with SHA256
- [x] All forms include CSRF tokens
- [x] CSRF middleware is enabled
- [x] Password validation enforced (8+ chars, complexity)
- [x] Email validation and uniqueness checking
- [x] Login required for profile access
- [x] Session management via Django's session framework
- [x] Pre-filled forms use Django template context escaping
- [x] No debug information exposed in production
- [x] Comprehensive security test suite

---

## 11. Future Security Enhancements

1. **Rate Limiting**: Implement `django-ratelimit` to prevent brute force attacks
2. **Two-Factor Authentication (2FA)**: Add TOTP-based 2FA using `django-otp`
3. **Email Verification**: Send verification emails on registration
4. **Password Reset Flow**: Secure password reset via email tokens
5. **Audit Logging**: Track login/logout events for security monitoring
6. **Account Lockout**: Temporary lockout after failed login attempts
7. **Security Headers**: Add CSP, HSTS headers via `django-csp`
8. **Permission-Based Access**: Implement granular permissions for actions

---

## 12. References

- [Django Security Documentation](https://docs.djangoproject.com/en/6.0/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PBKDF2 Algorithm](https://en.wikipedia.org/wiki/PBKDF2)
- [CSRF Protection](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

**Last Updated**: February 2026
**Django Version**: 6.0.1
**Python Version**: 3.14+
