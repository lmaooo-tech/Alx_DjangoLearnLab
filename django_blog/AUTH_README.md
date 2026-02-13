# Django Blog Authentication System

## Overview
This Django Blog project includes a comprehensive, secure authentication system with user registration, login, logout, and profile management. Built with Django's best practices for security and usability.

---

## Features

### ✓ User Registration
- Custom registration form with email field
- Optional first and last name
- Strong password validation (8+ characters, complexity requirements)
- Unique email enforcement
- Automatic UserProfile creation
- Immediate login after successful registration

### ✓ User Login
- Secure authentication using Django's built-in system
- Generic error messages (prevents user enumeration)
- Session-based authentication
- CSRF protection
- Remembers attempted redirect location

### ✓ User Logout
- Secure session cleanup
- Auto-redirect to login page
- One-click logout anywhere in the app

### ✓ Profile Management
- View user information
- Edit personal details (name, email)
- Profile picture upload (Pillow required)
- Add bio, location, and website
- Profile auto-created on user registration

### ✓ Security Features
- CSRF token protection on all forms
- Password hashing (PBKDF2 with SHA256)
- Password validation enforced
- Email validation and uniqueness
- Secure session management
- Login required decorator on protected views
- Input sanitization and validation

---

## Installation & Setup

### Prerequisites
- Python 3.14+
- Django 6.0+
- Pillow 12.1+ (for image upload)
- pip and virtual environment

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin panel)
python manage.py createsuperuser
```

### 3. Collect Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 4. Run Development Server
```bash
# Start development server
python manage.py runserver

# Access application
# http://localhost:8000
```

---

## URL Routes

### Authentication Routes
| Route | URL | View | Purpose |
|-------|-----|------|---------|
| register | `/register/` | `register` | User registration |
| login | `/login/` | `login_view` | User login |
| logout | `/logout/` | `logout_view` | User logout |
| profile | `/profile/` | `profile` | User profile (login required) |

### How to Use URLs in Templates
```html
<!-- Navigate to login -->
<a href="{% url 'login' %}">Login</a>

<!-- Navigate to registration -->
<a href="{% url 'register' %}">Register</a>

<!-- Navigate to profile (requires login) -->
<a href="{% url 'profile' %}">My Profile</a>

<!-- Logout -->
<a href="{% url 'logout' %}">Logout</a>
```

---

## User Flows

### Registration Flow
```
1. User clicks "Register" → /register/
2. Fills registration form
3. System validates:
   - Password strength (8+ chars, complexity)
   - Email format & uniqueness
   - Password confirmation match
4. User created if valid
5. UserProfile auto-created (via signal)
6. User auto-logged in
7. Redirected to /profile/
```

### Login Flow
```
1. User clicks "Login" → /login/
2. Enters username & password
3. Django's authenticate() function validates
4. If valid:
   - Session created
   - User logged in
   - Redirected to /profile/
5. If invalid:
   - Generic error shown
   - User stays on login page
```

### Profile Access Flow
```
1. Only authenticated users can access /profile/
2. Unauthenticated users redirected to login
3. Login page receives ?next=/profile/ parameter
4. After login, user redirected back to profile
```

### Logout Flow
```
1. User clicks "Logout"
2. Django's logout() destroys session
3. Session cookie deleted
4. User redirected to login page
```

---

## File Structure

```
django_blog/
├── blog/
│   ├── forms.py                 # CustomUserCreationForm, UserProfileForm
│   ├── models.py                # User, UserProfile, Post models
│   ├── views.py                 # register, login_view, logout_view, profile views
│   ├── urls.py                  # Authentication URL patterns
│   ├── admin.py                 # Admin interface configuration
│   ├── tests.py                 # Comprehensive test suite
│   ├── templates/blog/
│   │   ├── base.html            # Base template with conditional nav
│   │   ├── login.html           # Login form template
│   │   ├── register.html        # Registration form template
│   │   └── profile.html         # Profile view & edit template
│   └── static/css/
│       └── styles.css           # Authentication styling
├── django_blog/
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # Project URL routing
│   └── wsgi.py
├── SECURITY.md                  # Security documentation
├── TESTING.md                   # Testing guide
└── manage.py
```

---

## Configuration

### settings.py - Key Settings

```python
# Application Definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # Our app
]

# CSRF Protection
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    # ... other middleware
]

# Media Files (Profile Pictures)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication Settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]
```

### Production Security Settings
For deployment, update settings.py:

```python
# settings.py (Production)
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS & Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

---

## Code Examples

### Using Authentication in Views

```python
from django.contrib.auth.decorators import login_required

# Require user to be logged in
@login_required
def protected_view(request):
    return render(request, 'protected.html')

# Check if user is authenticated
def check_user_status(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return redirect('login')

# Get current user information
def user_profile_view(request):
    user = request.user
    email = user.email
    profile = user.profile
    bio = profile.bio
    return render(request, 'profile.html', {'user': user})
```

### Using Authentication in Templates

```html
<!-- Check if user is authenticated -->
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
    <a href="{% url 'profile' %}">My Profile</a>
    <a href="{% url 'logout' %}">Logout</a>
{% else %}
    <a href="{% url 'login' %}">Login</a>
    <a href="{% url 'register' %}">Register</a>
{% endif %}

<!-- Display user information -->
<p>Full Name: {{ user.get_full_name }}</p>
<p>Email: {{ user.email }}</p>
<p>Member Since: {{ user.date_joined|date:"F d, Y" }}</p>
```

### Form Usage Example

```python
from blog.forms import CustomUserCreationForm, UserProfileForm

# Registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Profile view
@login_required
def profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form})
```

---

## Testing

### Run Tests
```bash
# Run all authentication tests
python manage.py test blog

# Run specific test class
python manage.py test blog.tests.UserRegistrationTests

# Run with verbose output
python manage.py test blog -v 2

# Generate coverage report
coverage run --source='blog' manage.py test blog
coverage report
```

### Test Coverage
- Registration Tests: 7 test cases
- Login Tests: 6 test cases
- Logout Tests: 2 test cases
- Profile Tests: 5 test cases
- Password Security Tests: 2 test cases
- **Total**: 20+ test cases ensuring security and functionality

See [TESTING.md](TESTING.md) for detailed testing guide.

---

## Security Features

### Password Security
✓ Hashed with PBKDF2 + SHA256 (600,000+ iterations)
✓ Never stored in plaintext
✓ Validated on registration & profile update
✓ Django's password validators enforced

### CSRF Protection
✓ All forms include CSRF tokens
✓ CSRF middleware enabled
✓ Automatic validation on POST requests
✓ Double-submit cookie protection

### Session Security
✓ HTTP-only secure cookies
✓ Signed session data
✓ Session timeout configurable
✓ Session destroyed on logout

### Input Validation
✓ Email format & uniqueness validation
✓ Password complexity requirements
✓ Username validation
✓ Form data sanitization

See [SECURITY.md](SECURITY.md) for comprehensive security details.

---

## Common Tasks

### Change User Password
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.set_password('new_password_123')
user.save()
```

### Update User Profile
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.first_name = 'John'
user.last_name = 'Doe'
user.email = 'john@example.com'
user.save()

user.profile.bio = 'I love Django!'
user.profile.location = 'San Francisco'
user.profile.save()
```

### Delete User Account
```python
from django.contrib.auth.models import User

user = User.objects.get(username='john')
user.delete()  # UserProfile deleted automatically (CASCADE)
```

### Retrieve User Information
```python
from django.contrib.auth.models import User

# Get user by username
user = User.objects.get(username='john')

# Get user by email
user = User.objects.get(email='john@example.com')

# Get user profile
profile = user.profile
print(profile.bio)
print(profile.location)

# Get all users
users = User.objects.all()

# Search users
users = User.objects.filter(first_name__icontains='john')
```

---

## Troubleshooting

### Issue: "Pillow is not installed" error
```bash
# Solution: Install Pillow
pip install Pillow
```

### Issue: "Static files not found"
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput
```

### Issue: Database errors after model changes
```bash
# Solution: Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### Issue: CSRF token errors
```
# Solution: The {% csrf_token %} tag must be in all POST forms
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### Issue: User cannot login after registration
```
# Check:
1. User exists in database: User.objects.filter(username='username').exists()
2. Password is correct
3. No account limitations or locks
4. Session middleware is enabled
```

---

## Extending the Authentication System

### Add Email Verification
1. Install package: `pip install django-verify-email`
2. Create signal to send verification email on registration
3. Add verified field to UserProfile
4. Check verified flag before allowing certain actions

### Add Two-Factor Authentication
1. Install package: `pip install django-otp`
2. Add TOTP setup in user settings
3. Require TOTP code after password entry

### Add Social Authentication
1. Install package: `pip install django-allauth`
2. Configure Google/GitHub/Facebook OAuth
3. Link social accounts to user profile

### Add Rate Limiting
1. Install package: `pip install django-ratelimit`
2. Apply to login view to prevent brute force
3. Apply to registration to prevent spam

---

## Best Practices

### ✓ Do's
- ✓ Always validate user input on server-side
- ✓ Use HTTPS in production
- ✓ Hash passwords using Django's built-in functions
- ✓ Keep SECRET_KEY secret
- ✓ Use environment variables for sensitive config
- ✓ Enable all security middleware
- ✓ Keep Django updated
- ✓ Use CSRF tokens on all forms

### ✗ Don'ts
- ✗ Never store passwords in plaintext
- ✗ Don't expose user enumeration errors
- ✗ Don't trust client-side validation alone
- ✗ Don't disable CSRF protection
- ✗ Don't commit .env files to git
- ✗ Don't run DEBUG=True in production
- ✗ Don't use weak passwords in production
- ✗ Don't ignore security warnings

---

## Performance Considerations

- **Database Indexing**: Email field indexed for faster lookups
- **Session Caching**: Use cache backend for session store
- **Connection Pooling**: Configure database connection pool
- **Query Optimization**: Use select_related() for profile queries
- **Media Storage**: Use CDN for serving user images in production

---

## Resources

- [Django Authentication Documentation](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [Django Security Documentation](https://docs.djangoproject.com/en/6.0/topics/security/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [Django Forms Documentation](https://docs.djangoproject.com/en/6.0/topics/forms/)

---

## License
This project is provided for educational purposes.

## Support
For issues or questions, refer to:
- [SECURITY.md](SECURITY.md) - Security documentation
- [TESTING.md](TESTING.md) - Testing guide
- Django documentation: https://docs.djangoproject.com/

---

**Last Updated**: February 2026
**Django Version**: 6.0.1
**Status**: ✓ Production Ready
