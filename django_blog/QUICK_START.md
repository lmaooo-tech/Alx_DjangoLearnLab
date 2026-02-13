# Django Blog Authentication - Quick Start Guide

## 5-Minute Setup

### 1. Clone or Extract Project
```bash
cd c:\Users\HP\Alx_DjangoLearnLab\django_blog
```

### 2. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 6. Start Server
```bash
python manage.py runserver
```

### 7. Access Application
```
http://localhost:8000/
```

---

## First Time User Steps

### Register a New Account
1. Click **"Register"** in navigation
2. Fill in registration form:
   - Username: Choose a unique username
   - Email: Enter valid email address
   - Optional: First Name, Last Name
   - Password: 8+ characters with mixed case/numbers
   - Confirm Password: Must match password field
3. Click **"Register"** button
4. You'll be automatically logged in and redirected to profile

### Login to Account
1. Click **"Login"** in navigation
2. Enter username and password
3. Click **"Login"** button
4. You'll be redirected to your profile page

### Update Profile
1. Ensure you're logged in
2. Click your username in navigation or go to **/profile/**
3. Update any fields:
   - First Name / Last Name
   - Email (must be unique)
   - Bio (short description)
   - Location
   - Website
   - Profile Picture
4. Click **"Update Profile"** button
5. You'll see success message

### Logout
1. Click **"Logout"** in navigation
2. You'll be logged out and redirected to login page

---

## URL Quick Reference

| Action | URL | Status |
|--------|-----|--------|
| View Home | `/` | Public |
| Register | `/register/` | Public |
| Login | `/login/` | Public |
| Logout | `/logout/` | Login Required |
| Profile | `/profile/` | Login Required |
| Admin | `/admin/` | Admin Only |

---

## Testing the System

### Run Automated Tests
```bash
# Run all tests
python manage.py test blog

# Run only auth tests
python manage.py test blog.tests

# Verbose output
python manage.py test blog -v 2
```

### Manual Testing Checklist

- [ ] Can register with valid data
- [ ] Cannot register with duplicate email
- [ ] Cannot register with weak password
- [ ] Can login with correct credentials
- [ ] Cannot login with wrong credentials
- [ ] Can update profile information
- [ ] Can upload profile picture
- [ ] Can logout successfully
- [ ] Cannot access profile when logged out
- [ ] CSRF token visible in all forms

---

## Common Commands

### User Management
```bash
# Create user via command line
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('username', 'email@example.com', 'password')
>>> user.save()

# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.set_password('new_password')
>>> user.save()

# Delete user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.get(username='username').delete()
```

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Undo last migration
python manage.py migrate blog 0001  # Go back to migration 0001
```

### Debugging
```bash
# Django shell (interactive Python)
python manage.py shell

# Check installed apps
python manage.py diffsettings

# Validate project
python manage.py check

# View URL patterns
python manage.py show_urls
```

---

## Troubleshooting

### "Module not found" Error
```bash
# Solution: Install missing package
pip install -r requirements.txt
```

### "No database configured" Error
```bash
# Solution: Run migrations
python manage.py migrate
```

### "Permission denied" Error
```bash
# Solution: Check file permissions
# Windows: Run as Administrator
# macOS/Linux: Use sudo or check ownership
```

### "Port already in use" Error
```bash
# Solution: Use different port
python manage.py runserver 8001
```

### "Static files not found"
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput
```

---

## Environment Variables (Production)

Create `.env` file in project root:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Load in `settings.py`:
```python
from decouple import config
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
```

---

## File Locations

```
Project Root:
├── manage.py              # Django management command
├── requirements.txt       # Python dependencies
├── AUTH_README.md         # Full authentication guide
├── SECURITY.md            # Security documentation
├── TESTING.md             # Testing guide
├── QUICK_START.md         # This file
├── db.sqlite3             # Database (dev only)
├── media/                 # User uploads
├── static/                # CSS, JavaScript, Images
└── django_blog/
    ├── settings.py        # Django configuration
    ├── urls.py            # URL routing
    └── blog/
        ├── models.py      # Database models
        ├── views.py       # View functions
        ├── forms.py       # Form classes
        ├── urls.py        # App URL patterns
        └── templates/
            └── blog/
                ├── base.html
                ├── login.html
                ├── register.html
                └── profile.html
```

---

## Next Steps

1. **Read Full Documentation**: See [AUTH_README.md](AUTH_README.md) for complete guide
2. **Understand Security**: Review [SECURITY.md](SECURITY.md) for security features
3. **Run Tests**: Execute [TESTING.md](TESTING.md) test procedures
4. **Deploy**: Follow deployment guide in AUTH_README.md
5. **Extend**: Add features using developer guide

---

## Support Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django Authentication**: https://docs.djangoproject.com/en/6.0/topics/auth/
- **Security Best Practices**: https://docs.djangoproject.com/en/6.0/topics/security/
- **Project Issues**: Check project documentation

---

**Ready to go!** You now have a fully functional, secure authentication system. Start with registration, then login, and explore your profile. For more details, see [AUTH_README.md](AUTH_README.md).
