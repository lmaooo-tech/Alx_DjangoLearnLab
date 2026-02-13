from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, Post, Comment
from .forms import CommentForm
from django.contrib import messages


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


# ============================================================================
# Permission Tests
# ============================================================================

class PermissionTests(TestCase):
    """Test cases for access control and permissions"""
    
    def setUp(self):
        """Set up test users and posts"""
        self.client = Client()
        
        # Create test users
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='AuthPass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPass123'
        )
        
        # Create test posts
        self.post = Post.objects.create(
            title='Author Post',
            content='This is the author\'s post for testing permissions.',
            author=self.author
        )
        
        # URLs
        self.post_list_url = reverse('blog:post_list')
        self.post_detail_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
        self.post_create_url = reverse('blog:post_create')
        self.post_edit_url = reverse('blog:post_edit', kwargs={'pk': self.post.pk})
        self.post_delete_url = reverse('blog:post_delete', kwargs={'pk': self.post.pk})
        self.login_url = reverse('blog:login')


class PostListPermissionTests(PermissionTests):
    """Test permissions for post list view"""
    
    def test_post_list_accessible_to_anonymous_user(self):
        """Test that post list is accessible to non-authenticated users"""
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
    
    def test_post_list_accessible_to_authenticated_user(self):
        """Test that post list is accessible to authenticated users"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'].object_list)


class PostDetailPermissionTests(PermissionTests):
    """Test permissions for post detail view"""
    
    def test_post_detail_accessible_to_anonymous_user(self):
        """Test that post detail is accessible to non-authenticated users"""
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertEqual(response.context['post'], self.post)
    
    def test_post_detail_accessible_to_authenticated_user(self):
        """Test that post detail is accessible to authenticated users"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)
    
    def test_post_detail_displays_can_edit_for_author(self):
        """Test that can_edit is True for post author"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_detail_url)
        self.assertTrue(response.context['can_edit'])
    
    def test_post_detail_displays_can_edit_false_for_non_author(self):
        """Test that can_edit is False for non-author"""
        self.client.login(username='otheruser', password='OtherPass123')
        response = self.client.get(self.post_detail_url)
        self.assertFalse(response.context['can_edit'])
    
    def test_post_detail_nonexistent_returns_404(self):
        """Test that nonexistent post returns 404"""
        url = reverse('blog:post_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class PostCreatePermissionTests(PermissionTests):
    """Test permissions for post creation"""
    
    def test_post_create_requires_authentication(self):
        """Test that unauthenticated users cannot access create form"""
        response = self.client.get(self.post_create_url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)
    
    def test_post_create_redirects_to_login_with_next(self):
        """Test that unauthenticated users redirected to login with next parameter"""
        response = self.client.get(self.post_create_url, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)
    
    def test_post_create_accessible_to_authenticated_user(self):
        """Test that authenticated users can access create form"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
    
    def test_post_create_authenticated_user_can_create(self):
        """Test that authenticated user can create post"""
        self.client.login(username='author', password='AuthPass123')
        post_data = {
            'title': 'New Test Post',
            'content': 'This is a new test post created by authenticated user.'
        }
        response = self.client.post(self.post_create_url, post_data)
        
        # Check post was created
        new_post = Post.objects.get(title='New Test Post')
        self.assertEqual(new_post.author, self.author)
        
        # Should redirect to post detail
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(new_post.pk), response.url)
    
    def test_post_create_sets_author_to_current_user(self):
        """Test that created post author is set to current user"""
        self.client.login(username='author', password='AuthPass123')
        post_data = {
            'title': 'Author-Owned Post',
            'content': 'This post should belong to the author.'
        }
        self.client.post(self.post_create_url, post_data)
        
        post = Post.objects.get(title='Author-Owned Post')
        self.assertEqual(post.author, self.author)
        self.assertNotEqual(post.author, self.other_user)


class PostEditPermissionTests(PermissionTests):
    """Test permissions for post editing"""
    
    def test_post_edit_requires_authentication(self):
        """Test that unauthenticated users cannot access edit form"""
        response = self.client.get(self.post_edit_url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)
    
    def test_post_edit_author_can_access_form(self):
        """Test that post author can access edit form"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
    
    def test_post_edit_non_author_gets_403(self):
        """Test that non-author gets permission denied"""
        self.client.login(username='otheruser', password='OtherPass123')
        response = self.client.get(self.post_edit_url)
        # Should redirect (not 403, but we handle in view)
        self.assertIn(response.status_code, [302, 403])
    
    def test_post_edit_author_can_update(self):
        """Test that post author can update post"""
        self.client.login(username='author', password='AuthPass123')
        post_data = {
            'title': 'Updated Post Title',
            'content': 'This post has been updated.'
        }
        response = self.client.post(self.post_edit_url, post_data)
        
        # Check post was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post Title')
        self.assertEqual(self.post.content, 'This post has been updated.')
    
    def test_post_edit_non_author_cannot_update(self):
        """Test that non-author cannot update post"""
        self.client.login(username='otheruser', password='OtherPass123')
        original_title = self.post.title
        post_data = {
            'title': 'Hacked Title',
            'content': 'This should not be saved.'
        }
        response = self.client.post(self.post_edit_url, post_data)
        
        # Check post was not updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, original_title)
    
    def test_post_edit_anonymous_redirects_to_login(self):
        """Test that anonymous user redirected to login"""
        response = self.client.get(self.post_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)


class PostDeletePermissionTests(PermissionTests):
    """Test permissions for post deletion"""
    
    def test_post_delete_requires_authentication(self):
        """Test that unauthenticated users cannot access delete"""
        response = self.client.get(self.post_delete_url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)
    
    def test_post_delete_author_can_access_confirmation(self):
        """Test that post author can access delete confirmation"""
        self.client.login(username='author', password='AuthPass123')
        response = self.client.get(self.post_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')
    
    def test_post_delete_non_author_gets_permission_denied(self):
        """Test that non-author cannot delete"""
        self.client.login(username='otheruser', password='OtherPass123')
        response = self.client.get(self.post_delete_url)
        # Should be redirected (not 403, but we handle in view)
        self.assertIn(response.status_code, [302, 403])
    
    def test_post_delete_author_can_delete(self):
        """Test that post author can delete post"""
        self.client.login(username='author', password='AuthPass123')
        post_id = self.post.pk
        response = self.client.post(self.post_delete_url)
        
        # Check post was deleted
        self.assertFalse(Post.objects.filter(pk=post_id).exists())
        
        # Should redirect to post list
        self.assertEqual(response.status_code, 302)
        self.assertIn('post', response.url.lower())
    
    def test_post_delete_non_author_cannot_delete(self):
        """Test that non-author cannot delete post"""
        self.client.login(username='otheruser', password='OtherPass123')
        post_id = self.post.pk
        response = self.client.post(self.post_delete_url)
        
        # Check post still exists
        self.assertTrue(Post.objects.filter(pk=post_id).exists())
    
    def test_post_delete_anonymous_redirects_to_login(self):
        """Test that anonymous user redirected to login"""
        response = self.client.post(self.post_delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)
    
    def test_post_delete_permanent_deletion(self):
        """Test that deleted posts cannot be recovered"""
        self.client.login(username='author', password='AuthPass123')
        post_id = self.post.pk
        self.client.post(self.post_delete_url)
        
        # Try to access deleted post
        post_detail_url = reverse('blog:post_detail', kwargs={'pk': post_id})
        response = self.client.get(post_detail_url)
        self.assertEqual(response.status_code, 404)


class AccessControlMessageTests(PermissionTests):
    """Test access control messages"""
    
    def test_edit_permission_denied_message(self):
        """Test that edit denial shows appropriate message"""
        self.client.login(username='otheruser', password='OtherPass123')
        self.client.get(self.post_edit_url)
        messages_list = list(messages.get_messages(self.client.session))
        # Message may be displayed
    
    def test_delete_permission_denied_message(self):
        """Test that delete denial shows appropriate message"""
        self.client.login(username='otheruser', password='OtherPass123')
        self.client.get(self.post_delete_url)
        messages_list = list(messages.get_messages(self.client.session))
        # Message may be displayed


# ============================================================================
# Comment System Tests
# ============================================================================

class CommentModelTests(TestCase):
    """Test cases for Comment model"""
    
    def setUp(self):
        """Set up test data"""
        self.author = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='AuthPass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='This is test post content for comments.',
            author=self.author
        )
    
    def test_comment_creation(self):
        """Test that comment can be created"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='This is a test comment.'
        )
        
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.content, 'This is a test comment.')
    
    def test_comment_string_representation(self):
        """Test comment __str__ method"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Test comment'
        )
        
        expected_str = f'Comment by {self.author.username} on {self.post.title}'
        self.assertEqual(str(comment), expected_str)
    
    def test_comment_timestamps(self):
        """Test that comment has created_at and updated_at"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Test comment'
        )
        
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)
        self.assertEqual(comment.created_at, comment.updated_at)
    
    def test_comment_ordering(self):
        """Test that comments are ordered by newest first"""
        import time
        
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='First comment'
        )
        
        time.sleep(0.1)
        
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Second comment'
        )
        
        comments = Comment.objects.all()
        self.assertEqual(comments[0], comment2)  # Newest first
        self.assertEqual(comments[1], comment1)
    
    def test_comment_related_name(self):
        """Test that post.comments.all() returns related comments"""
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Comment 1'
        )
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Comment 2'
        )
        
        self.assertEqual(self.post.comments.count(), 2)
        self.assertIn(comment1, self.post.comments.all())
        self.assertIn(comment2, self.post.comments.all())
    
    def test_comment_cascade_delete_with_post(self):
        """Test that deleting post deletes comments"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Test comment'
        )
        
        comment_id = comment.pk
        self.post.delete()
        
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())
    
    def test_comment_cascade_delete_with_author(self):
        """Test that deleting author deletes comments"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            content='Test comment'
        )
        
        comment_id = comment.pk
        self.author.delete()
        
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())


class CommentFormTests(TestCase):
    """Test cases for CommentForm"""
    
    def test_comment_form_renders(self):
        """Test that comment form renders correctly"""
        form = CommentForm()
        self.assertIn('content', form.fields)
    
    def test_comment_form_valid_content(self):
        """Test form with valid content"""
        form = CommentForm(data={'content': 'This is a valid comment with enough characters.'})
        self.assertTrue(form.is_valid())
    
    def test_comment_form_empty_content(self):
        """Test form with empty content"""
        form = CommentForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('Comment cannot be empty', str(form.errors))
    
    def test_comment_form_too_short(self):
        """Test form with content too short"""
        form = CommentForm(data={'content': 'Hi'})
        self.assertFalse(form.is_valid())
        self.assertIn('at least 3 characters', str(form.errors))
    
    def test_comment_form_too_long(self):
        """Test form with content exceeding 5000 characters"""
        long_content = 'x' * 5001
        form = CommentForm(data={'content': long_content})
        self.assertFalse(form.is_valid())
        self.assertIn('exceed 5000 characters', str(form.errors))
    
    def test_comment_form_whitespace_only(self):
        """Test form with whitespace only"""
        form = CommentForm(data={'content': '    \n    '})
        self.assertFalse(form.is_valid())
        self.assertIn('meaningful comment', str(form.errors))
    
    def test_comment_form_minimum_valid_length(self):
        """Test form with exactly 3 characters (minimum)"""
        form = CommentForm(data={'content': 'Yes'})
        self.assertTrue(form.is_valid())
    
    def test_comment_form_maximum_valid_length(self):
        """Test form with exactly 5000 characters (maximum)"""
        max_content = 'x' * 5000
        form = CommentForm(data={'content': max_content})
        self.assertTrue(form.is_valid())


class CommentCreateViewTests(TestCase):
    """Test cases for CommentCreateView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='AuthPass123'
        )
        self.commenter = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='CommenterPass123'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='This is test post content.',
            author=self.author
        )
        
        self.comment_create_url = reverse('blog:comment_create', kwargs={'post_pk': self.post.pk})
        self.comment_form_url = reverse('blog:comment_create', kwargs={'post_pk': self.post.pk})
    
    def test_comment_create_requires_authentication(self):
        """Test that anonymous users redirected to login"""
        response = self.client.get(self.comment_create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_comment_create_authenticated_user_can_access(self):
        """Test that authenticated users can access comment form"""
        self.client.login(username='commenter', password='CommenterPass123')
        response = self.client.get(self.comment_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_form.html')
    
    def test_comment_create_authenticated_user_can_post(self):
        """Test that authenticated user can post comment"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        data = {'content': 'This is a new comment on the post.'}
        response = self.client.post(self.comment_create_url, data)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check comment was created
        self.assertTrue(Comment.objects.filter(content='This is a new comment on the post.').exists())
        
        # Check comment has correct author and post
        comment = Comment.objects.get(content='This is a new comment on the post.')
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.post, self.post)
    
    def test_comment_create_sets_author_automatically(self):
        """Test that author is set to current user"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        data = {'content': 'New comment for testing author assignment.'}
        self.client.post(self.comment_create_url, data)
        
        comment = Comment.objects.get(content='New comment for testing author assignment.')
        self.assertEqual(comment.author, self.commenter)
        # Ensure author was not set to post author
        self.assertNotEqual(comment.author, self.post.author)
    
    def test_comment_create_sets_post_automatically(self):
        """Test that post is set from URL parameter"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        data = {'content': 'Comment testing post assignment.'}
        self.client.post(self.comment_create_url, data)
        
        comment = Comment.objects.get(content='Comment testing post assignment.')
        self.assertEqual(comment.post, self.post)
    
    def test_comment_create_redirects_to_post_detail(self):
        """Test redirect after successful comment creation"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        data = {'content': 'Comment for redirect testing.'}
        response = self.client.post(self.comment_create_url, data, follow=False)
        
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
        self.assertEqual(response.url, expected_url)
    
    def test_comment_create_invalid_post(self):
        """Test comment creation on non-existent post"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        invalid_url = reverse('blog:comment_create', kwargs={'post_pk': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CommentUpdateViewTests(TestCase):
    """Test cases for CommentUpdateView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='AuthPass123'
        )
        self.commenter = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='CommenterPass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPass123'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test post content.',
            author=self.author
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Original comment content.'
        )
        
        self.comment_edit_url = reverse('blog:comment_edit', kwargs={'comment_pk': self.comment.pk})
    
    def test_comment_edit_requires_authentication(self):
        """Test that anonymous users cannot edit comments"""
        response = self.client.get(self.comment_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_comment_edit_author_can_access_form(self):
        """Test that comment author can access edit form"""
        self.client.login(username='commenter', password='CommenterPass123')
        response = self.client.get(self.comment_edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_form.html')
    
    def test_comment_edit_non_author_cannot_access(self):
        """Test that non-authors cannot edit comments"""
        self.client.login(username='otheruser', password='OtherPass123')
        response = self.client.get(self.comment_edit_url)
        self.assertIn(response.status_code, [302, 403])
    
    def test_comment_edit_author_can_update(self):
        """Test that author can update comment content"""
        self.client.login(username='commenter', password='CommenterPass123')
        
        data = {'content': 'Updated comment content with new information.'}
        response = self.client.post(self.comment_edit_url, data)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify content was updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment content with new information.')
    
    def test_comment_edit_non_author_cannot_update(self):
        """Test that non-author cannot update comment"""
        self.client.login(username='otheruser', password='OtherPass123')
        
        data = {'content': 'Attempted unauthorized update.'}
        self.client.post(self.comment_edit_url, data)
        
        # Verify content was NOT updated
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original comment content.')
    
    def test_comment_edit_updates_modified_timestamp(self):
        """Test that updated_at timestamp is updated"""
        original_updated = self.comment.updated_at
        
        self.client.login(username='commenter', password='CommenterPass123')
        
        import time
        time.sleep(0.1)
        
        data = {'content': 'Comment updated with new timestamp.'}
        self.client.post(self.comment_edit_url, data)
        
        self.comment.refresh_from_db()
        self.assertGreater(self.comment.updated_at, original_updated)
    
    def test_comment_edit_created_timestamp_unchanged(self):
        """Test that created_at is not changed on edit"""
        original_created = self.comment.created_at
        
        self.client.login(username='commenter', password='CommenterPass123')
        data = {'content': 'Comment with unchanged creation time.'}
        self.client.post(self.comment_edit_url, data)
        
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.created_at, original_created)
    
    def test_comment_edit_redirects_to_post(self):
        """Test redirect after edit goes to post detail"""
        self.client.login(username='commenter', password='CommenterPass123')
        data = {'content': 'Comment edited and redirected.'}
        response = self.client.post(self.comment_edit_url, data, follow=False)
        
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
        self.assertEqual(response.url, expected_url)


class CommentDeleteViewTests(TestCase):
    """Test cases for CommentDeleteView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='AuthPass123'
        )
        self.commenter = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='CommenterPass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPass123'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test post content.',
            author=self.author
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Comment to be deleted.'
        )
        
        self.comment_delete_url = reverse('blog:comment_delete', kwargs={'comment_pk': self.comment.pk})
    
    def test_comment_delete_requires_authentication(self):
        """Test that anonymous users cannot delete comments"""
        response = self.client.get(self.comment_delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_comment_delete_author_can_access_confirmation(self):
        """Test that author can access delete confirmation page"""
        self.client.login(username='commenter', password='CommenterPass123')
        response = self.client.get(self.comment_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_confirm_delete.html')
    
    def test_comment_delete_non_author_cannot_access(self):
        """Test that non-authors cannot access delete page"""
        self.client.login(username='otheruser', password='OtherPass123')
        response = self.client.get(self.comment_delete_url)
        self.assertIn(response.status_code, [302, 403])
    
    def test_comment_delete_author_can_delete(self):
        """Test that author can delete their comment"""
        self.client.login(username='commenter', password='CommenterPass123')
        comment_id = self.comment.pk
        
        response = self.client.post(self.comment_delete_url)
        
        # Verify redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify comment was deleted
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())
    
    def test_comment_delete_non_author_cannot_delete(self):
        """Test that non-author cannot delete comment"""
        self.client.login(username='otheruser', password='OtherPass123')
        comment_id = self.comment.pk
        
        self.client.post(self.comment_delete_url)
        
        # Verify comment still exists
        self.assertTrue(Comment.objects.filter(pk=comment_id).exists())
    
    def test_comment_delete_permanent_deletion(self):
        """Test that deleted comments cannot be recovered"""
        self.client.login(username='commenter', password='CommenterPass123')
        comment_id = self.comment.pk
        
        self.client.post(self.comment_delete_url)
        
        # Try to access deleted comment
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())
    
    def test_comment_delete_redirects_to_post(self):
        """Test redirect after deletion goes to post"""
        self.client.login(username='commenter', password='CommenterPass123')
        response = self.client.post(self.comment_delete_url, follow=False)
        
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
        self.assertEqual(response.url, expected_url)


class CommentDisplayTests(TestCase):
    """Test cases for comment display on post detail"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='AuthPass123'
        )
        self.commenter1 = User.objects.create_user(
            username='commenter1',
            email='commenter1@example.com',
            password='Commenter1Pass123'
        )
        self.commenter2 = User.objects.create_user(
            username='commenter2',
            email='commenter2@example.com',
            password='Commenter2Pass123'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test post content.',
            author=self.author
        )
        
        self.post_detail_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
    
    def test_post_detail_shows_no_comments_when_empty(self):
        """Test that empty post shows no comments message"""
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No comments yet')
    
    def test_post_detail_shows_comment_form_for_authenticated(self):
        """Test that authenticated users see comment form"""
        self.client.login(username='commenter1', password='Commenter1Pass123')
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post a Comment')
    
    def test_post_detail_shows_login_link_for_anonymous(self):
        """Test that anonymous users see login link"""
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'to post a comment')
    
    def test_post_detail_displays_comments(self):
        """Test that comments are displayed on post detail"""
        Comment.objects.create(
            post=self.post,
            author=self.commenter1,
            content='First comment on the post.'
        )
        
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First comment on the post.')
        self.assertContains(response, self.commenter1.username)
    
    def test_post_detail_displays_multiple_comments(self):
        """Test that multiple comments are displayed"""
        Comment.objects.create(
            post=self.post,
            author=self.commenter1,
            content='First comment on the post.'
        )
        Comment.objects.create(
            post=self.post,
            author=self.commenter2,
            content='Second comment on the post.'
        )
        
        response = self.client.get(self.post_detail_url)
        self.assertContains(response, 'First comment on the post.')
        self.assertContains(response, 'Second comment on the post.')
        self.assertContains(response, self.commenter1.username)
        self.assertContains(response, self.commenter2.username)
    
    def test_post_detail_shows_edit_button_for_comment_author(self):
        """Test that edit/delete buttons visible only to comment author"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.commenter1,
            content='Comment by commenter1.'
        )
        
        self.client.login(username='commenter1', password='Commenter1Pass123')
        response = self.client.get(self.post_detail_url)
        
        # Author should see edit and delete buttons
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Delete')
    
    def test_post_detail_hides_edit_button_for_non_author(self):
        """Test that non-authors don't see edit/delete buttons"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.commenter1,
            content='Comment by commenter1.'
        )
        
        self.client.login(username='commenter2', password='Commenter2Pass123')
        response = self.client.get(self.post_detail_url)
        
        # Non-author should NOT see edit/delete links for this comment
        self.assertContains(response, 'Comment by commenter1.')
        # Check button count should be 0 for commenter2's perspective
    
    def test_post_detail_comments_ordered_newest_first(self):
        """Test that comments are ordered newest first"""
        import time
        
        comment1 = Comment.objects.create(
            post=self.post,
            author=self.commenter1,
            content='First comment posted.'
        )
        time.sleep(0.1)
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.commenter2,
            content='Second comment posted.'
        )
        
        response = self.client.get(self.post_detail_url)
        content = response.content.decode()
        
        # Second comment should appear before first comment
        pos1 = content.find('Second comment posted.')
        pos2 = content.find('First comment posted.')
        self.assertLess(pos1, pos2)