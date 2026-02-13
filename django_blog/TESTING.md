# Authentication System Testing Guide

## Overview
This guide provides instructions for testing the Django Blog authentication system, including how to run automated tests and perform manual testing to verify security and functionality.

---

## 1. Automated Testing

### 1.1 Prerequisites
- Python 3.14+
- Django 6.0+
- All required packages installed
- Virtual environment activated

### 1.2 Running All Tests
```bash
# Navigate to project directory
cd django_blog

# Run all tests in the blog app
python manage.py test blog

# Run tests with verbose output
python manage.py test blog -v 2

# Run tests for authentication system specifically
python manage.py test blog.tests
```

### 1.3 Running Specific Test Classes

```bash
# User Registration Tests
python manage.py test blog.tests.UserRegistrationTests

# User Login Tests
python manage.py test blog.tests.UserLoginTests

# User Logout Tests
python manage.py test blog.tests.UserLogoutTests

# User Profile Tests
python manage.py test blog.tests.UserProfileTests

# Password Security Tests
python manage.py test blog.tests.PasswordSecurityTests
```

### 1.4 Running Individual Test Methods

```bash
# Test valid registration
python manage.py test blog.tests.UserRegistrationTests.test_registration_with_valid_data

# Test password security
python manage.py test blog.tests.PasswordSecurityTests.test_passwords_use_django_hashing

# Test CSRF protection
python manage.py test blog.tests.UserLoginTests.test_csrf_token_in_login_form
```

---

## 2. Test Coverage Report

### 2.1 Generate Coverage Report
```bash
# Install coverage tool
pip install coverage

# Run tests with coverage analysis
coverage run --source='blog' manage.py test blog

# Generate terminal report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

### 2.2 Expected Coverage
- **Forms**: 95%+ coverage
- **Views**: 90%+ coverage
- **Models**: 85%+ coverage
- **Overall**: 90%+ coverage target

---

## 3. Test Categories

### 3.1 User Registration Tests
Tests the account creation process with various scenarios:

**Test Methods:**
- `test_registration_page_loads`: Verifies registration page accessibility
- `test_registration_with_valid_data`: Tests successful registration
- `test_registration_with_duplicate_email`: Prevents duplicate emails
- `test_registration_with_mismatched_passwords`: Rejects password mismatches
- `test_registration_with_weak_password`: Enforces strong passwords
- `test_csrf_token_in_registration_form`: Validates CSRF token presence
- `test_registered_user_can_login`: Verifies registered users can login

**Key Verifications:**
✓ User created in database
✓ Email uniqueness enforced
✓ Password hashing applied
✓ CSRF token present
✓ Form validation works

### 3.2 User Login Tests
Tests the authentication and session creation:

**Test Methods:**
- `test_login_page_loads`: Verifies login page accessibility
- `test_login_with_valid_credentials`: Tests successful authentication
- `test_login_with_invalid_username`: Prevents non-existent user access
- `test_login_with_invalid_password`: Prevents wrong password access
- `test_csrf_token_in_login_form`: Validates CSRF token presence
- `test_password_not_in_response`: Security check - password never displayed

**Key Verifications:**
✓ Session created after successful login
✓ User redirected to profile page
✓ Invalid credentials rejected
✓ CSRF token present
✓ Password never visible in responses

### 3.3 User Logout Tests
Tests session cleanup and redirect:

**Test Methods:**
- `test_logout_redirects_to_login`: Verifies redirect to login page
- `test_user_not_authenticated_after_logout`: Confirms session destruction

**Key Verifications:**
✓ Session data cleared
✓ User redirected to login
✓ Protected pages require re-authentication

### 3.4 User Profile Tests
Tests profile access and update functionality:

**Test Methods:**
- `test_profile_requires_login`: Enforces authentication requirement
- `test_authenticated_user_can_access_profile`: Verifies profile access
- `test_csrf_token_in_profile_form`: Validates CSRF token presence
- `test_update_profile_information`: Tests profile data updates
- `test_duplicate_email_in_profile_update_rejected`: Prevents email conflicts

**Key Verifications:**
✓ Profile page requires login
✓ Profile data updates correctly
✓ Email uniqueness maintained
✓ CSRF token present

### 3.5 Password Security Tests
Tests password handling and security:

**Test Methods:**
- `test_passwords_use_django_hashing`: Verifies PBKDF2 hashing
- `test_password_validation_enforced`: Ensures strong password requirements

**Key Verifications:**
✓ Passwords hashed with PBKDF2
✓ Weak passwords rejected
✓ Password validators active

---

## 4. Manual Testing Workflow

### 4.1 Test Registration Flow

1. **Access Registration Page**
   ```
   URL: http://localhost:8000/register/
   Expected: Registration form displayed
   ```

2. **Test With Valid Data**
   - Username: `testuser1`
   - Email: `testuser1@example.com`
   - First Name: `John`
   - Last Name: `Doe`
   - Password: `SecurePassword123!@#`
   - Confirm Password: `SecurePassword123!@#`
   - Expected: User created, redirected to profile

3. **Test With Duplicate Email**
   - Register with already-used email
   - Expected: Error message displayed, user not created

4. **Test With Weak Password**
   - Password: `123`
   - Expected: Validation error, user not created

5. **Test With Mismatched Passwords**
   - Password: `Password123!@#`
   - Confirm: `DifferentPassword123!@#`
   - Expected: Validation error, user not created

❌ **Expected Errors:**
- Duplicate email: "This email address is already registered."
- Weak password: "This password is too short. It must contain at least 8 characters."
- Mismatch: "The two password fields didn't match."

### 4.2 Test Login Flow

1. **Access Login Page**
   ```
   URL: http://localhost:8000/login/
   Expected: Login form displayed
   ```

2. **Test With Valid Credentials**
   - Username: `testuser1`
   - Password: `SecurePassword123!@#`
   - Expected: User logged in, redirected to profile

3. **Test With Invalid Username**
   - Username: `nonexistent`
   - Password: `SecurePassword123!@#`
   - Expected: Generic error message

4. **Test With Invalid Password**
   - Username: `testuser1`
   - Password: `WrongPassword`
   - Expected: Generic error message

❌ **Expected Error:**
- "Invalid username or password."

### 4.3 Test Profile Management Flow

1. **Access Profile Page (Authenticated)**
   ```
   URL: http://localhost:8000/profile/
   Expected: User profile displayed with edit form
   ```

2. **Update Profile Information**
   - First Name: `Jane`
   - Email: `newemail@example.com`
   - Bio: `Hello, I'm a Django developer!`
   - Location: `San Francisco, CA`
   - Website: `https://example.com`
   - Expected: Profile updated, success message shown

3. **Test Profile Access Without Login**
   ```
   Logout first
   Try to access: http://localhost:8000/profile/
   Expected: Redirect to login page
   ```

4. **Upload Profile Picture** (if enabled)
   - Select image file (JPG, PNG)
   - Expected: Image uploaded and displayed

### 4.4 Test Logout Flow

1. **Click Logout Button**
   - Expected: User logged out, redirected to login page

2. **Try to Access Profile**
   - Expected: Redirect to login page with next parameter

### 4.5 Test CSRF Protection

1. **Verify CSRF Token in Forms**
   ```html
   Inspect login form → Look for: <input type="hidden" name="csrfmiddlewaretoken" value="...">
   ```

2. **Test CSRF Token Validation**
   - Open browser DevTools
   - Edit CSRF token value before submission
   - Expected: Form submission fails with 403 Forbidden

---

## 5. Security Verification Checklist

### 5.1 Password Security
- [ ] Passwords are hashed (check database: `SELECT * FROM auth_user;`)
- [ ] Passwords visible as hash format (e.g., `pbkdf2_sha256$...`)
- [ ] Weak passwords rejected on registration
- [ ] Changing password updates hash correctly

### 5.2 CSRF Protection
- [ ] CSRF token present in all forms
- [ ] Tampering with token causes 403 error
- [ ] Token changes on each page load
- [ ] Token matches between form and cookie

### 5.3 Session Security
- [ ] Session cookie set with secure flags
- [ ] Session destroyed on logout
- [ ] Cannot access protected pages without login
- [ ] Old session ID invalid after logout

### 5.4 Input Validation
- [ ] Email format validated (invalid emails rejected)
- [ ] Email uniqueness enforced
- [ ] Username format validated
- [ ] Special characters handled safely

### 5.5 Error Handling
- [ ] Generic error messages (no user enumeration)
- [ ] Stack traces not visible in production
- [ ] Helpful error messages in development
- [ ] No sensitive data in error pages

---

## 6. Performance Testing

### 6.1 Load Test (Example using Locust)
```bash
# Install locust
pip install locust

# Create locustfile.py with test scenarios
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### 6.2 Expected Response Times (Development)
- Registration: < 500ms
- Login: < 300ms
- Profile page load: < 200ms
- Profile update: < 500ms

---

## 7. Browser Compatibility Testing

Test the authentication system in:
- ✓ Chrome 60+
- ✓ Firefox 55+
- ✓ Safari 11+
- ✓ Edge 79+
- ✓ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 8. Accessibility Testing

### 8.1 Form Accessibility
- [ ] All form fields have labels
- [ ] Error messages are linked to fields
- [ ] Required fields are marked
- [ ] Password inputs hidden but visible on request

### 8.2 WCAG Compliance
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast sufficient (WCAG AA)
- [ ] Focus indicators visible

---

## 9. Integration Testing

### 9.1 Database Integration
```python
# Test database operations
from django.contrib.auth.models import User
from blog.models import UserProfile

# Verify signal creates profile
user = User.objects.create_user(username='test', password='pass')
assert hasattr(user, 'profile')  # Profile auto-created
```

### 9.2 Email Integration (if implemented)
- [ ] Confirmation emails sent
- [ ] Email contains verification link
- [ ] Link works and verifies email
- [ ] Unverified users cannot do certain actions

---

## 10. Debugging Failed Tests

### 10.1 Common Issues

**Issue**: Test fails with "User not found"
```bash
Solution: Ensure test user is created in setUp() method
```

**Issue**: Test fails with "CSRF token missing"
```bash
Solution: Use Django test client which handles CSRF automatically
```

**Issue**: Test fails with "Redirect not matched"
```bash
Solution: Check URL names are correct and views return proper redirects
```

### 10.2 Debug Tips
```python
# Add debug output in tests
def test_login(self):
    print(f"User exists: {User.objects.filter(username='testuser').exists()}")
    response = self.client.post(self.login_url, data)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
```

### 10.3 Run Single Test with Debug
```bash
python manage.py test blog.tests.UserLoginTests.test_login_with_valid_credentials --debug-mode
```

---

## 11. Continuous Integration

### 11.1 GitHub Actions Example
```yaml
name: Django Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test blog
```

---

## 12. Testing Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Test Names**: Describe what the test verifies
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External APIs**: Don't rely on external services
5. **Use Fixtures**: Reuse common test data
6. **Test Edge Cases**: Empty inputs, special characters, boundary values
7. **Clean Up**: Remove test data after each test
8. **Documentation**: Add docstrings explaining complex tests

---

## 13. Test Execution Summary

```
Total Test Cases: 20+
- Registration Tests: 7
- Login Tests: 6
- Logout Tests: 2
- Profile Tests: 5
- Password Security Tests: 2

Coverage Target: 90%+
Execution Time: < 10 seconds
Success Criteria: All tests pass
```

---

**Last Updated**: February 2026
**Django Version**: 6.0+
**Test Framework**: Django TestCase (built-in)
