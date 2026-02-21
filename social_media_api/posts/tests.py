from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Post, Comment

User = get_user_model()


class PostAPITestCase(TestCase):
    """Test suite for Post API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create tokens for users
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        # Create test posts
        self.post1 = Post.objects.create(
            author=self.user1,
            title='Django Tutorial',
            content='Learn Django REST Framework basics'
        )
        self.post2 = Post.objects.create(
            author=self.user2,
            title='Python Tips',
            content='Advanced Python programming techniques'
        )

    def test_list_posts(self):
        """Test listing all posts (public access)."""
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_post_authenticated(self):
        """Test creating a post (authenticated users only)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        data = {
            'title': 'API Design Patterns',
            'content': 'Best practices for RESTful API design'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'testuser1 (user1@test.com)')
        self.assertEqual(Post.objects.count(), 3)

    def test_create_post_unauthenticated(self):
        """Test that unauthenticated users cannot create posts."""
        data = {
            'title': 'Unauthorized Post',
            'content': 'This should fail'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_post(self):
        """Test retrieving a single post with comments."""
        response = self.client.get(f'/api/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Django Tutorial')
        self.assertEqual(response.data['author'], 'testuser1 (user1@test.com)')

    def test_update_own_post(self):
        """Test that authors can update their own posts."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        data = {
            'title': 'Updated Django Tutorial',
            'content': 'Updated content'
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Updated Django Tutorial')

    def test_update_other_post(self):
        """Test that users cannot update posts by other users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        data = {
            'title': 'Hacked Title',
            'content': 'Hacked content'
        }
        response = self.client.put(
            f'/api/posts/{self.post1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_post(self):
        """Test that authors can delete their own posts."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.delete(f'/api/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_other_post(self):
        """Test that users cannot delete posts by other users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        response = self.client.delete(f'/api/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_posts_by_author(self):
        """Test filtering posts by author."""
        response = self.client.get('/api/posts/?author=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['author'], 'testuser1 (user1@test.com)')

    def test_search_posts(self):
        """Test searching posts by title and content."""
        # Search by title
        response = self.client.get('/api/posts/?search=Django')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('Django', response.data['results'][0]['title'])
        
        # Search by content
        response = self.client.get('/api/posts/?search=programming')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('programming', response.data['results'][0]['content'])

    def test_pagination(self):
        """Test pagination of posts."""
        # Create multiple posts
        for i in range(15):
            Post.objects.create(
                author=self.user1,
                title=f'Post {i}',
                content=f'Content {i}'
            )
        
        # First page
        response = self.client.get('/api/posts/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        
        # Second page
        response = self.client.get('/api/posts/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    def test_ordering_posts(self):
        """Test ordering of posts."""
        # Order by newest first (default)
        response = self.client.get('/api/posts/?ordering=-created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Python Tips')
        
        # Order by oldest first
        response = self.client.get('/api/posts/?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Django Tutorial')


class CommentAPITestCase(TestCase):
    """Test suite for Comment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create tokens for users
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        # Create test post
        self.post = Post.objects.create(
            author=self.user1,
            title='Test Post',
            content='Test content'
        )
        
        # Create test comments
        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Great post!'
        )
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user2,
            content='Very informative'
        )

    def test_list_comments(self):
        """Test listing all comments (public access)."""
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_comment_authenticated(self):
        """Test creating a comment (authenticated users only)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        data = {
            'post': self.post.id,
            'content': 'Excellent explanation!'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'testuser2 (user2@test.com)')
        self.assertEqual(Comment.objects.count(), 3)

    def test_create_comment_unauthenticated(self):
        """Test that unauthenticated users cannot create comments."""
        data = {
            'post': self.post.id,
            'content': 'Unauthorized comment'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_comment(self):
        """Test retrieving a single comment."""
        response = self.client.get(f'/api/comments/{self.comment1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Great post!')
        self.assertEqual(response.data['author'], 'testuser1 (user1@test.com)')

    def test_update_own_comment(self):
        """Test that authors can update their own comments."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        data = {'content': 'Updated comment'}
        response = self.client.put(
            f'/api/comments/{self.comment1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.content, 'Updated comment')

    def test_update_other_comment(self):
        """Test that users cannot update comments by other users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        data = {'content': 'Hacked comment'}
        response = self.client.put(
            f'/api/comments/{self.comment2.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_comment(self):
        """Test that authors can delete their own comments."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.delete(f'/api/comments/{self.comment1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_other_comment(self):
        """Test that users cannot delete comments by other users."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.delete(f'/api/comments/{self.comment2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_comments_by_author(self):
        """Test filtering comments by author."""
        response = self.client.get('/api/comments/?author=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['author'], 'testuser1 (user1@test.com)')

    def test_filter_comments_by_post(self):
        """Test filtering comments by post."""
        response = self.client.get(f'/api/comments/?post={self.post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_comments(self):
        """Test searching comments by content."""
        response = self.client.get('/api/comments/?search=Great')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Great post!')

    def test_pagination_comments(self):
        """Test pagination of comments."""
        # Create multiple comments
        for i in range(15):
            Comment.objects.create(
                post=self.post,
                author=self.user1,
                content=f'Comment {i}'
            )
        
        # First page
        response = self.client.get('/api/comments/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        
        # Second page
        response = self.client.get('/api/comments/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    def test_post_comments_endpoint(self):
        """Test the /posts/{id}/comments/ endpoint."""
        response = self.client.get(f'/api/posts/{self.post.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class DataIntegrityTestCase(TestCase):
    """Test suite for data integrity and relationships."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_post_CASCADE_delete(self):
        """Test that deleting a post also deletes its comments."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content='Test comment'
        )
        
        self.assertEqual(Comment.objects.count(), 1)
        
        # Delete the post
        response = self.client.delete(f'/api/posts/{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify comment is also deleted
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_count_in_post(self):
        """Test that comment count is correctly reflected in post response."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        
        # Initially no comments
        response = self.client.get(f'/api/posts/{post.id}/')
        self.assertEqual(response.data['comments_count'], 0)
        
        # Add a comment
        Comment.objects.create(
            post=post,
            author=self.user,
            content='Test comment'
        )
        
        # Verify comment count increased
        response = self.client.get(f'/api/posts/{post.id}/')
        self.assertEqual(response.data['comments_count'], 1)

    def test_read_only_fields(self):
        """Test that read-only fields cannot be modified."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test content'
        )
        
        # Try to modify read-only fields
        data = {
            'title': 'Modified',
            'content': 'Modified content',
            'id': 999,  # Try to change ID
            'created_at': '2020-01-01T00:00:00Z'  # Try to change timestamp
        }
        response = self.client.put(
            f'/api/posts/{post.id}/',
            data,
            format='json'
        )
        
        # Verify only modifiable fields changed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], post.id)  # ID unchanged
        self.assertEqual(response.data['title'], 'Modified')

    def test_author_assignment_on_create(self):
        """Test that author is automatically set to current user on creation."""
        data = {
            'title': 'New Post',
            'content': 'New content'
        }
        response = self.client.post('/api/posts/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'testuser (test@test.com)')
        
        post = Post.objects.get(id=response.data['id'])
        self.assertEqual(post.author, self.user)

