from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile


class UserRegistrationTests(TestCase):
    """Test cases for user registration functionality"""
    
    def setUp(self):
        """Set up test client and URL"""
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
    
    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html')
    
    def test_registration_with_valid_data(self):
        """Test successful user registration with valid data"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'SecurePass123!@#',
            'password2': 'SecurePass123!@#',
        }
        response = self.client.post(self.register_url, data)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
    
    def test_registration_with_duplicate_email(self):
        """Test that duplicate email registration is rejected"""
        # Create first user
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        
        # Try to register with same email
        data = {
            'username': 'user2',
            'email': 'test@example.com',
            'password1': 'SecurePass123!@#',
            'password2': 'SecurePass123!@#',
        }
        response = self.client.post(self.register_url, data)
        
        # Should not create second user
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)
    
    def test_registration_with_mismatched_passwords(self):
        """Test that mismatched passwords are rejected"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'SecurePass123!@#',
            'password2': 'DifferentPass123!@#',
        }
        response = self.client.post(self.register_url, data)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_registration_with_weak_password(self):
        """Test that weak passwords are rejected"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': '123',
            'password2': '123',
        }
        response = self.client.post(self.register_url, data)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_csrf_token_in_registration_form(self):
        """Test that CSRF token is present in registration form"""
        response = self.client.get(self.register_url)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_registered_user_can_login(self):
        """Test that newly registered user can login"""
        # Register user
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'SecurePass123!@#',
            'password2': 'SecurePass123!@#',
        }
        self.client.post(self.register_url, data)
        
        # Try to login
        login_data = {
            'username': 'testuser',
            'password': 'SecurePass123!@#',
        }
        response = self.client.post(self.login_url, login_data)
        
        # Check user is authenticated (redirected to profile)
        self.assertRedirects(response, self.profile_url)


class UserLoginTests(TestCase):
    """Test cases for user login functionality"""
    
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.logout_url = reverse('logout')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/login.html')
    
    def test_login_with_valid_credentials(self):
        """Test successful login with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123',
        }
        response = self.client.post(self.login_url, data)
        
        # Check user is authenticated
        self.assertRedirects(response, self.profile_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_invalid_username(self):
        """Test login with invalid username"""
        data = {
            'username': 'invaliduser',
            'password': 'TestPassword123',
        }
        response = self.client.post(self.login_url, data)
        
        # Should not redirect (should redisplay login page)
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_invalid_password(self):
        """Test login with invalid password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword',
        }
        response = self.client.post(self.login_url, data)
        
        # Should not redirect (should redisplay login page)
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_token_in_login_form(self):
        """Test that CSRF token is present in login form"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_password_not_in_response(self):
        """Test that password is never displayed in response"""
        response = self.client.get(self.login_url)
        self.assertNotContains(response, 'TestPassword123')


class UserLogoutTests(TestCase):
    """Test cases for user logout functionality"""
    
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
        
        # Create and login test user
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        self.client.login(username='testuser', password='TestPassword123')
    
    def test_logout_redirects_to_login(self):
        """Test that logout redirects to login page"""
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
    
    def test_user_not_authenticated_after_logout(self):
        """Test that user is not authenticated after logout"""
        # First verify user is authenticated
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.get(self.logout_url)
        
        # Try to access profile - should redirect to login
        response = self.client.get(profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={profile_url}')


class UserProfileTests(TestCase):
    """Test cases for user profile functionality"""
    
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.profile_url = reverse('profile')
        self.login_url = reverse('login')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        # UserProfile should be auto-created via signal
        self.profile = self.user.profile
    
    def test_profile_requires_login(self):
        """Test that profile page requires authentication"""
        response = self.client.get(self.profile_url)
        
        # Should redirect to login
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')
    
    def test_authenticated_user_can_access_profile(self):
        """Test that authenticated user can access profile page"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/profile.html')
    
    def test_csrf_token_in_profile_form(self):
        """Test that CSRF token is present in profile form"""
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.get(self.profile_url)
        
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_update_profile_information(self):
        """Test updating user profile information"""
        self.client.login(username='testuser', password='TestPassword123')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'bio': 'Hello, this is my bio',
            'location': 'New York',
            'website': 'https://example.com',
        }
        response = self.client.post(self.profile_url, data)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        # Check updates
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.profile.bio, 'Hello, this is my bio')
        self.assertEqual(self.profile.location, 'New York')
        self.assertEqual(self.profile.website, 'https://example.com')
    
    def test_duplicate_email_in_profile_update_rejected(self):
        """Test that duplicate email is rejected during profile update"""
        # Create second user
        User.objects.create_user(
            username='testuser2',
            email='existing@example.com',
            password='TestPassword123'
        )
        
        # Try to update first user's email to existing email
        self.client.login(username='testuser', password='TestPassword123')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'existing@example.com',
            'bio': 'Hello, this is my bio',
            'location': 'New York',
            'website': 'https://example.com',
        }
        response = self.client.post(self.profile_url, data)
        
        # Email should not be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')


class PasswordSecurityTests(TestCase):
    """Test cases for password security"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_passwords_use_django_hashing(self):
        """Test that passwords are hashed using Django's algorithm"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            password='TestPassword123'
        )
        
        # Password should be hashed, not plaintext
        self.assertNotEqual(user.password, 'TestPassword123')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_password_validation_enforced(self):
        """Test that password validation is enforced"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'test',  # Too simple
            'password2': 'test',
        }
        response = self.client.post(self.register_url, data)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser').exists())
