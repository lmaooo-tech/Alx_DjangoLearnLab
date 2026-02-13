# Django Blog Authentication - Developer Guide

## Introduction
This guide is for developers who want to understand, modify, or extend the authentication system built into Django Blog.

---

## Architecture Overview

### Component Diagram
```
┌─────────────────────────────────────────────────────┐
│                   User Browser                       │
└─────────────────────┬───────────────────────────────┘
                      │
                      ↓
        ┌─────────────────────────────┐
        │    Django URL Routing       │
        │  (blog/urls.py)             │
        └──────────┬──────────────────┘
                   │
        ┌──────────┴──────────────────────────────────┐
        ↓              ↓              ↓               ↓
    ┌────────┐   ┌────────┐   ┌────────┐       ┌────────┐
    │Register│   │ Login  │   │Logout  │       │Profile │
    │ View   │   │ View   │   │ View   │       │ View   │
    └───┬────┘   └───┬────┘   └───┬────┘       └───┬────┘
        │            │            │                │
        ↓            ↓            ↓                ↓
    ┌───────────────────────────────────────────────────────┐
    │         Authentication Forms (blog/forms.py)          │
    │  - CustomUserCreationForm                             │
    │  - UserProfileForm                                    │
    └───────┬───────────────────────────────────────────────┘
            │
            ↓
    ┌───────────────────────────────────────────────────────┐
    │         Django Models (blog/models.py)                │
    │  - User (built-in)                                    │
    │  - UserProfile (custom)                               │
    │  - Post                                               │
    └───────┬───────────────────────────────────────────────┘
            │
            ↓
    ┌───────────────────────────────────────────────────────┐
    │            SQLite Database                            │
    │  - auth_user table                                    │
    │  - blog_userprofile table                             │
    └───────────────────────────────────────────────────────┘
```

---

## Code Structure

### Views (`blog/views.py`)

```python
# Registration View
def register(request):
    """
    Handles user registration
    - GET: Display registration form
    - POST: Process form submission
    Flow: Form validation → User creation → Profile auto-creation → Auto-login → Redirect
    """

# Login View
def login_view(request):
    """
    Handles user login
    - Authenticates user credentials
    - Creates session
    - Handles "next" parameter for redirect
    """

# Logout View
def logout_view(request):
    """
    Handles user logout
    - Destroys session
    - Redirects to login page
    """

# Profile View
@login_required
def profile(request):
    """
    User profile display and editing
    - Requires login
    - Displays user information
    - Allows profile updates
    - Handles file uploads
    """
```

### Forms (`blog/forms.py`)

```python
# CustomUserCreationForm
# Extends Django's UserCreationForm
# Adds email field and validation
# Validates unique email

# UserProfileForm
# Allows editing of extended profile fields
# Links to both User and UserProfile models
# Validates email uniqueness
```

### Models (`blog/models.py`)

```python
# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField()
    location = models.CharField()
    website = models.URLField()
    
# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)
```

### Templates

```
blog/templates/blog/
├── base.html          # Base template with conditional nav
├── login.html         # Login form
├── register.html      # Registration form
└── profile.html       # Profile view & edit form
```

---

## Key Concepts

### 1. Django's Built-in Authentication

Django provides:
- `User` model with username, email, password
- `authenticate()` function for credential validation
- `login()` / `logout()` functions for session management
- `LoginRequired` decorator for view protection
- Password hashing (PBKDF2)

### 2. One-to-One Relationship

```python
# UserProfile extends User with OneToOne relationship
user = User.objects.get(username='john')
profile = user.profile  # Access via reverse relation
```

### 3. Signal Handlers

```python
# Auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
```

### 4. CSRF Protection

Every form includes:
```html
<form method="post">
    {% csrf_token %}  <!-- Prevents CSRF attacks -->
</form>
```

### 5. Password Hashing

Django automatically hashes passwords using PBKDF2:
```python
user = User.objects.create_user('username', 'email', 'password')
# Password automatically hashed
```

---

## Extending the Authentication System

### Add Email Verification

**Step 1: Create email verification model**
```python
# In blog/models.py
from django.utils import timezone
from datetime import timedelta

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def is_token_valid(self):
        expiry = self.created_at + timedelta(hours=24)
        return timezone.now() < expiry
```

**Step 2: Send verification email**
```python
# In blog/views.py
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

def register(request):
    if form.is_valid():
        user = form.save()
        token = get_random_string(50)
        EmailVerification.objects.create(user=user, token=token)
        
        verification_link = f"http://yourdomain.com/verify/{token}"
        send_mail(
            'Verify your email',
            f'Click here to verify: {verification_link}',
            'noreply@yourdomain.com',
            [user.email]
        )
        login(request, user)
        return redirect('profile')
```

**Step 3: Create verification view**
```python
def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token)
        if verification.is_token_valid():
            verification.is_verified = True
            verification.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('profile')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link')
    return redirect('login')
```

### Add Two-Factor Authentication

**Install package:**
```bash
pip install django-otp qrcode
```

**Configure settings.py:**
```python
INSTALLED_APPS = [
    'django_otp',
    'django_otp.plugins.otp_totp',
]

MIDDLEWARE = [
    'django_otp.middleware.OTPMiddleware',  # Enable OTP
]
```

**Create TOTP setup view:**
```python
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import StaticDevice

@login_required
def setup_2fa(request):
    device = StaticDevice.objects.create(user=request.user)
    qr_code = device.generate_challenge()
    return render(request, '2fa_setup.html', {'qr_code': qr_code})

@otp_required
def protected_view(request):
    # Only accessible after OTP verification
    return render(request, 'protected.html')
```

### Add Social Authentication

**Install package:**
```bash
pip install django-allauth
```

**Configure settings.py:**
```python
INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
```

**Add to URLs:**
```python
urlpatterns = [
    path('accounts/', include('allauth.urls')),
]
```

### Add Rate Limiting

**Install package:**
```bash
pip install django-ratelimit
```

**Apply to login view:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Max 5 login attempts per minute per IP
    ...
```

### Add Passwordless Authentication

**Using email links:**
```python
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode

def email_login_request(request):
    email = request.POST.get('email')
    try:
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())
        
        link = f"http://yourdomain.com/auth/link/{uid}/{token}"
        send_mail(
            'Your Login Link',
            f'Click to login: {link}',
            'noreply@yourdomain.com',
            [email]
        )
    except User.DoesNotExist:
        pass  # Security: don't reveal if email exists
```

---

## Customizing Authentication

### Change Password Requirements

In `settings.py`:
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}  # Increase to 12
    },
    # ... other validators
]
```

### Customize Login Redirect

In `settings.py`:
```python
LOGIN_REDIRECT_URL = 'dashboard'  # Custom URL name
LOGOUT_REDIRECT_URL = 'homepage'  # Custom URL name
```

### Add Custom User Fields

**Create custom User model:**
```python
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
```

**Update settings.py:**
```python
AUTH_USER_MODEL = 'blog.CustomUser'
```

### Customize Templates

**Extend base.html:**
```html
{% extends 'blog/base.html' %}

{% block title %}Custom Title{% endblock %}

{% block content %}
    <!-- Your custom content -->
{% endblock %}
```

---

## Testing Custom Authentication

### Unit Tests

```python
from django.test import TestCase
from django.contrib.auth.models import User

class CustomAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='pass123'
        )
    
    def test_custom_feature(self):
        # Test your custom feature
        pass
```

### Integration Tests

```python
from django.test import Client

def test_full_flow(self):
    client = Client()
    
    # Register
    response = client.post('/register/', {...})
    self.assertEqual(response.status_code, 302)
    
    # Login
    response = client.post('/login/', {...})
    self.assertEqual(response.status_code, 302)
    
    # Access protected page
    response = client.get('/profile/')
    self.assertEqual(response.status_code, 200)
```

---

## Performance Optimization

### Database Optimization

```python
# Use select_related for one-to-one
users = User.objects.select_related('profile').all()

# Use prefetch_related for reverse queries
profiles = UserProfile.objects.prefetch_related('user').all()

# Add database indexes
class UserProfile(models.Model):
    email = models.EmailField(db_index=True)  # Index for faster lookups
```

### Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def profile(request):
    ...
```

### Query Optimization

```python
# Avoid N+1 queries
# BAD:
for user in User.objects.all():
    print(user.profile.bio)  # Query for each user!

# GOOD:
users = User.objects.select_related('profile')
for user in users:
    print(user.profile.bio)  # No extra queries
```

---

## Security Hardening

### Add Rate Limiting
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    ...
```

### Add Account Lockout
```python
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def is_locked(cls, user):
        attempts = cls.objects.filter(
            user=user,
            timestamp__gte=timezone.now() - timedelta(minutes=15)
        ).count()
        return attempts >= 5
```

### Add Security Headers
```python
# In settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),
    "style-src": ("'self'", "'unsafe-inline'"),
}
```

---

## Debugging & Troubleshooting

### Check User Authentication State

```python
# In view
if request.user.is_authenticated:
    print(f"Logged in as: {request.user.username}")
else:
    print("User not authenticated")
```

### Database Inspection

```bash
python manage.py shell

# Check user
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='john').values()

# Check profile
>>> from blog.models import UserProfile
>>> UserProfile.objects.filter(user__username='john').values()

# Check password hash
>>> user = User.objects.get(username='john')
>>> user.password  # Shows hash, not plaintext
```

### Reset Password

```python
# In shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='john')
>>> user.set_password('newpassword123')
>>> user.save()
```

### Clear Sessions

```bash
python manage.py clearsessions
```

---

## Documentation Guidelines

When extending the authentication system:

1. **Document new features** in docstrings
2. **Update AUTH_README.md** with new capabilities
3. **Add tests** for new functionality
4. **Update SECURITY.md** if security-related
5. **Create migration guide** for upgrades

---

## Common Pitfalls to Avoid

❌ **Don't** store passwords in plaintext
❌ **Don't** disable CSRF protection
❌ **Don't** skip password validation
❌ **Don't** expose user enumeration errors
❌ **Don't** skip testing security changes
❌ **Don't** mix authentication logic in templates
❌ **Don't** forget to hash passwords: `user.set_password()`

✅ **Do** use Django's built-in auth functions
✅ **Do** test all authentication paths
✅ **Do** keep security documentation updated
✅ **Do** follow Django security best practices
✅ **Do** use environment variables for secrets
✅ **Do** implement rate limiting
✅ **Do** audit access logs

---

## Resources for Developers

- [Django Authentication System](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [Django Models Documentation](https://docs.djangoproject.com/en/6.0/topics/db/models/)
- [Django Forms Documentation](https://docs.djangoproject.com/en/6.0/topics/forms/)
- [Django Signals](https://docs.djangoproject.com/en/6.0/topics/signals/)
- [Django Testing](https://docs.djangoproject.com/en/6.0/topics/testing/)
- [OWASP Authentication Guide](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

**Happy coding!** Refer back to this guide when extending or customizing the authentication system.
