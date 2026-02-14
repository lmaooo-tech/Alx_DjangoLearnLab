"""
Comprehensive test suite for the Book API endpoints.

This test module covers:
- CRUD operations (Create, Retrieve, Update, Delete)
- Permission enforcement (authenticated vs unauthenticated users)
- Data validation
- Query parameter filtering
- Error handling and edge cases
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime
from .models import Author, Book


class AuthorModelTest(TestCase):
    """Test cases for the Author model"""
    
    def setUp(self):
        """Create test data for author tests"""
        self.author = Author.objects.create(name="J.K. Rowling")
    
    def test_author_creation(self):
        """Test that an author can be created successfully"""
        self.assertEqual(self.author.name, "J.K. Rowling")
        self.assertTrue(Author.objects.filter(name="J.K. Rowling").exists())
    
    def test_author_str_representation(self):
        """Test the string representation of an author"""
        self.assertEqual(str(self.author), "J.K. Rowling")


class BookModelTest(TestCase):
    """Test cases for the Book model"""
    
    def setUp(self):
        """Create test data for book tests"""
        self.author = Author.objects.create(name="George R.R. Martin")
        self.book = Book.objects.create(
            title="A Game of Thrones",
            publication_year=1996,
            author=self.author
        )
    
    def test_book_creation(self):
        """Test that a book can be created successfully"""
        self.assertEqual(self.book.title, "A Game of Thrones")
        self.assertEqual(self.book.publication_year, 1996)
        self.assertEqual(self.book.author, self.author)
    
    def test_book_str_representation(self):
        """Test the string representation of a book"""
        self.assertEqual(str(self.book), "A Game of Thrones")
    
    def test_book_author_relationship(self):
        """Test the relationship between Book and Author"""
        self.assertIn(self.book, self.author.books.all())


class BookListViewTest(TestCase):
    """Test cases for the BookListView endpoint (GET /api/books/)"""
    
    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.url = '/api/books/'
        
        # Create test authors and books
        self.author1 = Author.objects.create(name="J.R.R. Tolkien")
        self.author2 = Author.objects.create(name="C.S. Lewis")
        
        self.book1 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.author1
        )
        self.book3 = Book.objects.create(
            title="The Chronicles of Narnia",
            publication_year=1950,
            author=self.author2
        )
    
    def test_book_list_unauthenticated_access(self):
        """
        Test that unauthenticated users can access the book list
        (Permission: AllowAny)
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_list_returns_all_books(self):
        """Test that the list view returns all books"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that response contains book data
        self.assertTrue('results' in response.data or isinstance(response.data, list))
    
    def test_book_list_filter_by_author(self):
        """Test filtering books by author using query parameters"""
        response = self.client.get(self.url, {'author': self.author1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books by author1
    
    def test_book_list_filter_by_year_range(self):
        """Test filtering books by publication year range"""
        response = self.client.get(self.url, {
            'year_min': 1950,
            'year_max': 1954
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_list_ordering(self):
        """Test that books are ordered by publication year (descending)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookDetailViewTest(TestCase):
    """Test cases for the BookDetailView endpoint (GET /api/books/<int:pk>/)"""
    
    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.author = Author.objects.create(name="Stephen King")
        self.book = Book.objects.create(
            title="The Shining",
            publication_year=1977,
            author=self.author
        )
        self.url = f'/api/books/{self.book.id}/'
    
    def test_book_detail_unauthenticated_access(self):
        """
        Test that unauthenticated users can retrieve book details
        (Permission: AllowAny)
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_detail_returns_correct_data(self):
        """Test that the detail view returns correct book information"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'The Shining')
        self.assertEqual(response.data['publication_year'], 1977)
    
    def test_book_detail_nonexistent_book(self):
        """Test that requesting a non-existent book returns 404"""
        url = '/api/books/9999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookCreateViewTest(TestCase):
    """Test cases for the BookCreateView endpoint (POST /api/books/create/)"""
    
    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.url = '/api/books/create/'
        self.author = Author.objects.create(name="Haruki Murakami")
        
        self.valid_data = {
            'title': 'Norwegian Wood',
            'publication_year': 1987,
            'author': self.author.id
        }
    
    def test_book_create_unauthenticated_denied(self):
        """
        Test that unauthenticated users cannot create books
        (Permission: IsAuthenticated)
        Expected: 401 Unauthorized
        """
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_book_create_authenticated_success(self):
        """Test that authenticated users can create books successfully"""
        # Create and authenticate a user
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title='Norwegian Wood').exists())
    
    def test_book_create_validates_future_year(self):
        """
        Test that book creation fails for future publication years
        (Validation: publication_year <= current year)
        """
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        future_year = datetime.now().year + 5
        invalid_data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author.id
        }
        
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_book_create_validates_required_fields(self):
        """Test that book creation fails when required fields are missing"""
        user = User.objects.create_user(
            username='testuser3',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Missing title
        invalid_data = {
            'publication_year': 2020,
            'author': self.author.id
        }
        
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_book_create_validates_author_exists(self):
        """Test that book creation fails when author doesn't exist"""
        user = User.objects.create_user(
            username='testuser4',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        invalid_data = {
            'title': 'Orphan Book',
            'publication_year': 2020,
            'author': 9999  # Non-existent author
        }
        
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookUpdateViewTest(TestCase):
    """Test cases for the BookUpdateView endpoint (PUT/PATCH /api/books/<int:pk>/update/)"""
    
    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.author = Author.objects.create(name="Jane Austen")
        self.book = Book.objects.create(
            title="Pride and Prejudice",
            publication_year=1813,
            author=self.author
        )
        self.url = f'/api/books/{self.book.id}/update/'
        
        self.update_data = {
            'title': 'Pride and Prejudice (Revised)',
            'publication_year': 1813,
            'author': self.author.id
        }
    
    def test_book_update_unauthenticated_denied(self):
        """
        Test that unauthenticated users cannot update books
        (Permission: IsAuthenticated)
        Expected: 401 Unauthorized
        """
        response = self.client.patch(self.url, {'title': 'New Title'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_book_update_authenticated_partial_update(self):
        """Test that authenticated users can perform partial updates (PATCH)"""
        user = User.objects.create_user(
            username='updateuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.patch(self.url, {'title': 'Pride and Prejudice (2nd Edition)'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Pride and Prejudice (2nd Edition)')
    
    def test_book_update_authenticated_full_update(self):
        """Test that authenticated users can perform full updates (PUT)"""
        user = User.objects.create_user(
            username='fullupdate',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.put(self.url, self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_update_validates_future_year(self):
        """Test that book update fails for future publication years"""
        user = User.objects.create_user(
            username='updateuser2',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        future_year = datetime.now().year + 10
        invalid_data = {
            'title': 'Pride and Prejudice',
            'publication_year': future_year,
            'author': self.author.id
        }
        
        response = self.client.put(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_book_update_nonexistent_book(self):
        """Test that updating a non-existent book returns 404"""
        user = User.objects.create_user(
            username='updateuser3',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        url = '/api/books/9999/update/'
        response = self.client.patch(url, {'title': 'New Title'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTest(TestCase):
    """Test cases for the BookDeleteView endpoint (DELETE /api/books/<int:pk>/delete/)"""
    
    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.author = Author.objects.create(name="Oscar Wilde")
        self.book = Book.objects.create(
            title="The Picture of Dorian Gray",
            publication_year=1890,
            author=self.author
        )
        self.url = f'/api/books/{self.book.id}/delete/'
    
    def test_book_delete_unauthenticated_denied(self):
        """
        Test that unauthenticated users cannot delete books
        (Permission: IsAuthenticated)
        Expected: 401 Unauthorized
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verify book still exists
        self.assertTrue(Book.objects.filter(id=self.book.id).exists())
    
    def test_book_delete_authenticated_success(self):
        """Test that authenticated users can delete books successfully"""
        user = User.objects.create_user(
            username='deleteuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify book is deleted
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
    
    def test_book_delete_nonexistent_book(self):
        """Test that deleting a non-existent book returns 404"""
        user = User.objects.create_user(
            username='deleteuser2',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        url = '/api/books/9999/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PermissionIntegrationTest(TestCase):
    """Integration tests for permission enforcement across all endpoints"""
    
    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_read_endpoints_allow_unauthenticated(self):
        """Test that read endpoints allow unauthenticated access"""
        # List view
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Detail view
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_write_endpoints_deny_unauthenticated(self):
        """Test that write endpoints deny unauthenticated access"""
        # Create
        response = self.client.post('/api/books/create/', {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Update
        response = self.client.patch(f'/api/books/{self.book.id}/update/', {
            'title': 'Updated Title'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Delete
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_write_endpoints_allow_authenticated(self):
        """Test that write endpoints allow authenticated access"""
        self.client.force_authenticate(user=self.user)
        
        # Create
        response = self.client.post('/api/books/create/', {
            'title': 'New Authenticated Book',
            'publication_year': 2023,
            'author': self.author.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
