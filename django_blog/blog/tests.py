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

# ============================================================================
# Form Tests
# ============================================================================

from .forms import PostForm, PostSearchForm, PostFilterForm
from .models import Post


class PostFormTests(TestCase):
    """Test cases for PostForm"""
    
    def setUp(self):
        """Set up test user and form"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_post_form_valid_data(self):
        """Test PostForm with valid data"""
        form_data = {
            'title': 'Test Blog Post',
            'content': 'This is a comprehensive test blog post content.'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_post_form_invalid_empty_title(self):
        """Test PostForm rejects empty title"""
        form_data = {
            'title': '',
            'content': 'This is test content.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_post_form_invalid_short_title(self):
        """Test PostForm rejects title shorter than 3 chars"""
        form_data = {
            'title': 'AB',
            'content': 'This is test content.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_post_form_invalid_long_title(self):
        """Test PostForm rejects title longer than 200 chars"""
        form_data = {
            'title': 'A' * 201,
            'content': 'This is test content.'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_post_form_invalid_special_chars_in_title(self):
        """Test PostForm rejects special characters in title"""
        invalid_titles = [
            'Test <Post>',
            'Test {Post}',
            'Test < Post >',
        ]
        for title in invalid_titles:
            form_data = {
                'title': title,
                'content': 'This is test content.'
            }
            form = PostForm(data=form_data)
            self.assertFalse(form.is_valid(), f"Form accepted invalid title: {title}")
            self.assertIn('title', form.errors)
    
    def test_post_form_invalid_empty_content(self):
        """Test PostForm rejects empty content"""
        form_data = {
            'title': 'Test Post',
            'content': ''
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_post_form_invalid_short_content(self):
        """Test PostForm rejects content shorter than 10 chars"""
        form_data = {
            'title': 'Test Post',
            'content': 'Short'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_post_form_strips_whitespace(self):
        """Test PostForm strips whitespace from title and content"""
        form_data = {
            'title': '  Test Post  ',
            'content': '  This is test content with spaces.  '
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Test Post')
        self.assertEqual(form.cleaned_data['content'], 'This is test content with spaces.')
    
    def test_post_form_requires_title_and_content(self):
        """Test that both title and content are required"""
        form_data = {'title': '', 'content': ''}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('content', form.errors)
    
    def test_post_form_prevents_identical_title_content(self):
        """Test PostForm prevents content being only the title"""
        form_data = {
            'title': 'Test',
            'content': 'Test'  # Same as title
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_post_form_widgets_have_bootstrap_classes(self):
        """Test that form widgets have Bootstrap classes"""
        form = PostForm()
        self.assertIn('form-control', str(form['title'].field.widget.attrs))
        self.assertIn('form-control', str(form['content'].field.widget.attrs))
    
    def test_post_form_has_help_text(self):
        """Test that form fields have help text"""
        form = PostForm()
        self.assertIsNotNone(form.fields['title'].help_text)
        self.assertIsNotNone(form.fields['content'].help_text)
        self.assertIn('200', form.fields['title'].help_text)
        self.assertIn('10', form.fields['content'].help_text)


class PostSearchFormTests(TestCase):
    """Test cases for PostSearchForm"""
    
    def test_search_form_empty_valid(self):
        """Test PostSearchForm accepts empty search"""
        form_data = {'q': ''}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_search_form_valid_query(self):
        """Test PostSearchForm with valid search query"""
        form_data = {'q': 'django blog'}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_search_form_rejects_single_char(self):
        """Test PostSearchForm rejects single character query"""
        form_data = {'q': 'a'}
        form = PostSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_search_form_accepts_two_chars(self):
        """Test PostSearchForm accepts 2 character query"""
        form_data = {'q': 'ab'}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_search_form_rejects_too_long_query(self):
        """Test PostSearchForm rejects query longer than 200 chars"""
        form_data = {'q': 'a' * 201}
        form = PostSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_search_form_strips_whitespace(self):
        """Test PostSearchForm strips whitespace"""
        form_data = {'q': '  django  '}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['q'], 'django')
    
    def test_search_form_widget_has_bootstrap(self):
        """Test search form widget has Bootstrap class"""
        form = PostSearchForm()
        self.assertIn('form-control', str(form['q'].field.widget.attrs))


class PostFilterFormTests(TestCase):
    """Test cases for PostFilterForm"""
    
    def test_filter_form_default_sort(self):
        """Test PostFilterForm defaults to newest"""
        form_data = {}
        form = PostFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['sort_by'], 'newest')
    
    def test_filter_form_valid_sort_options(self):
        """Test PostFilterForm accepts all valid sort options"""
        valid_sorts = ['newest', 'oldest', 'title_asc', 'title_desc']
        for sort_option in valid_sorts:
            form_data = {'sort_by': sort_option}
            form = PostFilterForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Failed for sort_by={sort_option}")
    
    def test_filter_form_invalid_sort_option(self):
        """Test PostFilterForm rejects invalid sort option"""
        form_data = {'sort_by': 'invalid_sort'}
        form = PostFilterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('sort_by', form.errors)
    
    def test_filter_form_widget_is_select(self):
        """Test filter form has select widget"""
        form = PostFilterForm()
        self.assertIn('form-control', str(form['sort_by'].field.widget.attrs))
    
    def test_filter_form_has_all_choices(self):
        """Test filter form displays all sort options"""
        form = PostFilterForm()
        choices = [choice[0] for choice in form.fields['sort_by'].choices]
        self.assertIn('newest', choices)
        self.assertIn('oldest', choices)
        self.assertIn('title_asc', choices)
        self.assertIn('title_desc', choices)


class PostCRUDFormIntegrationTests(TestCase):
    """Integration tests for PostForm with CRUD operations"""
    
    def setUp(self):
        """Set up test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.client.login(username='testuser', password='TestPass123')
        self.create_url = reverse('post_create')
        self.list_url = reverse('post_list')
    
    def test_create_post_with_form(self):
        """Test creating a post via form"""
        post_data = {
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content for testing.'
        }
        response = self.client.post(self.create_url, post_data, follow=True)
        
        # Check post was created
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'Test Blog Post')
        self.assertEqual(post.author, self.user)
    
    def test_create_post_author_auto_set(self):
        """Test that post author is automatically set to current user"""
        post_data = {
            'title': 'Test Post',
            'content': 'Test content for author verification.'
        }
        self.client.post(self.create_url, post_data)
        
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
    
    def test_search_functionality(self):
        """Test search functionality with PostSearchForm"""
        # Create test posts
        user = User.objects.get(username='testuser')
        Post.objects.create(
            title='Django Tutorial',
            content='A comprehensive Django tutorial for beginners.',
            author=user
        )
        Post.objects.create(
            title='Python Tips',
            content='Useful Python programming tips and tricks.',
            author=user
        )
        
        # Search for Django
        response = self.client.get(self.list_url, {'q': 'Django'})
        self.assertContains(response, 'Django Tutorial')
        self.assertNotContains(response, 'Python Tips')
    
    def test_filter_sort_newest(self):
        """Test filtering posts by newest first"""
        user = User.objects.get(username='testuser')
        post1 = Post.objects.create(
            title='First Post',
            content='First post content here for testing.',
            author=user
        )
        post2 = Post.objects.create(
            title='Second Post',
            content='Second post content here for testing.',
            author=user
        )
        
        response = self.client.get(self.list_url, {'sort_by': 'newest'})
        posts = list(response.context['posts'])
        self.assertEqual(posts[0].id, post2.id)  # Newer first
        self.assertEqual(posts[1].id, post1.id)
    
    def test_filter_sort_oldest(self):
        """Test filtering posts by oldest first"""
        user = User.objects.get(username='testuser')
        post1 = Post.objects.create(
            title='First Post',
            content='First post content here for testing.',
            author=user
        )
        post2 = Post.objects.create(
            title='Second Post',
            content='Second post content here for testing.',
            author=user
        )
        
        response = self.client.get(self.list_url, {'sort_by': 'oldest'})
        posts = list(response.context['posts'])
        self.assertEqual(posts[0].id, post1.id)  # Older first
    
    def test_filter_sort_by_title_asc(self):
        """Test filtering posts by title ascending"""
        user = User.objects.get(username='testuser')
        Post.objects.create(
            title='Zebra Post',
            content='Zebra post content here for testing.',
            author=user
        )
        Post.objects.create(
            title='Apple Post',
            content='Apple post content here for testing.',
            author=user
        )
        
        response = self.client.get(self.list_url, {'sort_by': 'title_asc'})
        posts = list(response.context['posts'])
        self.assertEqual(posts[0].title, 'Apple Post')
        self.assertEqual(posts[1].title, 'Zebra Post')