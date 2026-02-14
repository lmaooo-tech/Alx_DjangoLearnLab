"""
Unit tests for API endpoints in the advanced-api-project.

Tests cover:
- CRUD operations for Book model
- Filtering functionality
- Search functionality
- Ordering functionality
- Permissions and authentication
- Data validation
"""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from datetime import datetime
from .models import Author, Book


class BookAPITestCase(APITestCase):
    """Base test case with common setup for Book API tests."""
    
    def setUp(self):
        """Set up test data and clients."""
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            is_staff=True
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name="John Smith")
        self.author2 = Author.objects.create(name="Jane Doe")
        self.author3 = Author.objects.create(name="Robert Johnson")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="Django for Beginners",
            publication_year=2020,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="Python Programming",
            publication_year=2019,
            author=self.author2
        )
        self.book3 = Book.objects.create(
            title="Advanced Django",
            publication_year=2022,
            author=self.author1
        )
        self.book4 = Book.objects.create(
            title="REST API Design",
            publication_year=2021,
            author=self.author3
        )
        
        # Set up clients
        self.client = APIClient()
        self.authenticated_client = APIClient()
        self.authenticated_client.force_authenticate(user=self.user)
        
        # Alternative: Client with login for session-based auth
        self.logged_in_client = APIClient()
        self.logged_in_client.login(username='testuser', password='testpass123')
        
        # URL endpoints
        self.list_url = reverse('book-list')
        self.create_url = reverse('book-create')


class BookListViewTests(BookAPITestCase):
    """Tests for BookListView - retrieving list of books."""
    
    def test_list_books_unauthenticated(self):
        """Test that unauthenticated users can view book list."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
    
    def test_list_books_authenticated(self):
        """Test that authenticated users can view book list."""
        response = self.authenticated_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
    
    def test_list_books_returns_correct_data(self):
        """Test that book list returns correct book data."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that response contains expected fields
        first_book = response.data['results'][0]
        self.assertIn('id', first_book)
        self.assertIn('title', first_book)
        self.assertIn('publication_year', first_book)
        self.assertIn('author', first_book)


class BookDetailViewTests(BookAPITestCase):
    """Tests for BookDetailView - retrieving single book."""
    
    def test_retrieve_book_unauthenticated(self):
        """Test that unauthenticated users can view book details."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
    
    def test_retrieve_book_authenticated(self):
        """Test that authenticated users can view book details."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.authenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
    
    def test_retrieve_nonexistent_book(self):
        """Test retrieving a book that doesn't exist returns 404."""
        url = reverse('book-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_book_returns_correct_data(self):
        """Test that book detail returns all expected fields."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Django for Beginners")
        self.assertEqual(response.data['publication_year'], 2020)
        self.assertEqual(response.data['author'], self.author1.pk)


class BookCreateViewTests(BookAPITestCase):
    """Tests for BookCreateView - creating new books."""
    
    def test_create_book_unauthenticated(self):
        """Test that unauthenticated users cannot create books."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated(self):
        """Test that authenticated users can create books."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 5)
        self.assertEqual(response.data['title'], 'New Book')
    
    def test_create_book_with_future_year(self):
        """Test that creating a book with future publication year fails."""
        current_year = datetime.now().year
        data = {
            'title': 'Future Book',
            'publication_year': current_year + 1,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
    
    def test_create_book_missing_required_fields(self):
        """Test that creating a book without required fields fails."""
        data = {
            'title': 'Incomplete Book'
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_book_with_invalid_author(self):
        """Test that creating a book with invalid author ID fails."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': 9999
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookUpdateViewTests(BookAPITestCase):
    """Tests for BookUpdateView - updating existing books."""
    
    def test_update_book_unauthenticated(self):
        """Test that unauthenticated users cannot update books."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated Title',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated(self):
        """Test that authenticated users can update books."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated Django Book',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = self.authenticated_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Django Book')
    
    def test_partial_update_book(self):
        """Test that PATCH requests work for partial updates."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {'title': 'Partially Updated Title'}
        response = self.authenticated_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Partially Updated Title')
        self.assertEqual(self.book1.publication_year, 2020)  # Unchanged
    
    def test_update_nonexistent_book(self):
        """Test that updating a nonexistent book returns 404."""
        url = reverse('book-update', kwargs={'pk': 9999})
        data = {
            'title': 'Updated Title',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = self.authenticated_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTests(BookAPITestCase):
    """Tests for BookDeleteView - deleting books."""
    
    def test_delete_book_unauthenticated(self):
        """Test that unauthenticated users cannot delete books."""
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book1.pk).exists())
    
    def test_delete_book_authenticated(self):
        """Test that authenticated users can delete books."""
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.authenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book1.pk).exists())
        self.assertEqual(Book.objects.count(), 3)
    
    def test_delete_nonexistent_book(self):
        """Test that deleting a nonexistent book returns 404."""
        url = reverse('book-delete', kwargs={'pk': 9999})
        response = self.authenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookFilteringTests(BookAPITestCase):
    """Tests for filtering functionality."""
    
    def test_filter_by_title(self):
        """Test filtering books by title."""
        response = self.client.get(self.list_url, {'title': 'django'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 books with "Django"
    
    def test_filter_by_author_id(self):
        """Test filtering books by author ID."""
        response = self.client.get(self.list_url, {'author': self.author1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 books by author1
    
    def test_filter_by_author_name(self):
        """Test filtering books by author name."""
        response = self.client.get(self.list_url, {'author_name': 'smith'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Books by John Smith
    
    def test_filter_by_publication_year(self):
        """Test filtering books by exact publication year."""
        response = self.client.get(self.list_url, {'publication_year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['publication_year'], 2020)
    
    def test_filter_by_publication_year_min(self):
        """Test filtering books by minimum publication year."""
        response = self.client.get(self.list_url, {'publication_year_min': 2021})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books from 2021 and 2022
        years = [book['publication_year'] for book in response.data['results']]
        self.assertTrue(all(year >= 2021 for year in years))
    
    def test_filter_by_publication_year_max(self):
        """Test filtering books by maximum publication year."""
        response = self.client.get(self.list_url, {'publication_year_max': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books from 2019 and 2020
        years = [book['publication_year'] for book in response.data['results']]
        self.assertTrue(all(year <= 2020 for year in years))
    
    def test_filter_by_year_range(self):
        """Test filtering books by publication year range."""
        response = self.client.get(
            self.list_url,
            {'publication_year_min': 2020, 'publication_year_max': 2021}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertTrue(all(2020 <= year <= 2021 for year in years))
    
    def test_multiple_filters(self):
        """Test applying multiple filters simultaneously."""
        response = self.client.get(
            self.list_url,
            {'author_name': 'smith', 'publication_year_min': 2020}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books by Smith from 2020 onwards
        self.assertEqual(len(response.data['results']), 2)


class BookSearchTests(BookAPITestCase):
    """Tests for search functionality."""
    
    def test_search_by_title(self):
        """Test searching books by title."""
        response = self.client.get(self.list_url, {'search': 'python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        titles = [book['title'] for book in response.data['results']]
        self.assertTrue(any('Python' in title for title in titles))
    
    def test_search_by_author_name(self):
        """Test searching books by author name."""
        response = self.client.get(self.list_url, {'search': 'jane'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response1 = self.client.get(self.list_url, {'search': 'DJANGO'})
        response2 = self.client.get(self.list_url, {'search': 'django'})
        self.assertEqual(
            len(response1.data['results']),
            len(response2.data['results'])
        )
    
    def test_search_no_results(self):
        """Test searching with term that has no matches."""
        response = self.client.get(self.list_url, {'search': 'nonexistentterm'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_search_with_multiple_terms(self):
        """Test searching with multiple terms."""
        response = self.client.get(self.list_url, {'search': 'django rest'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find books with either term


class BookOrderingTests(BookAPITestCase):
    """Tests for ordering functionality."""
    
    def test_order_by_title_ascending(self):
        """Test ordering books by title in ascending order."""
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))
    
    def test_order_by_title_descending(self):
        """Test ordering books by title in descending order."""
        response = self.client.get(self.list_url, {'ordering': '-title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles, reverse=True))
    
    def test_order_by_publication_year_ascending(self):
        """Test ordering books by publication year ascending."""
        response = self.client.get(self.list_url, {'ordering': 'publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years))
    
    def test_order_by_publication_year_descending(self):
        """Test ordering books by publication year descending."""
        response = self.client.get(self.list_url, {'ordering': '-publication_year'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_default_ordering(self):
        """Test that default ordering is by title."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))


class BookCombinedQueryTests(BookAPITestCase):
    """Tests for combining filtering, searching, and ordering."""
    
    def test_filter_and_search(self):
        """Test combining filtering and searching."""
        response = self.client.get(
            self.list_url,
            {'author_name': 'smith', 'search': 'django'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return Django books by Smith
    
    def test_filter_and_order(self):
        """Test combining filtering and ordering."""
        response = self.client.get(
            self.list_url,
            {'author_name': 'smith', 'ordering': '-publication_year'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_search_and_order(self):
        """Test combining searching and ordering."""
        response = self.client.get(
            self.list_url,
            {'search': 'django', 'ordering': 'publication_year'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years))
    
    def test_filter_search_and_order(self):
        """Test combining filtering, searching, and ordering."""
        response = self.client.get(
            self.list_url,
            {
                'publication_year_min': 2020,
                'search': 'django',
                'ordering': '-title'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookPermissionsTests(BookAPITestCase):
    """Tests for permissions and authentication."""
    
    def test_list_permission_unauthenticated(self):
        """Test that list endpoint is accessible without authentication."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_detail_permission_unauthenticated(self):
        """Test that detail endpoint is accessible without authentication."""
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_permission_unauthenticated(self):
        """Test that create endpoint requires authentication."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_permission_unauthenticated(self):
        """Test that update endpoint requires authentication."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated Title',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_permission_unauthenticated(self):
        """Test that delete endpoint requires authentication."""
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_authenticated_user_can_create(self):
        """Test that authenticated users can create books."""
        data = {
            'title': 'Authenticated User Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_authenticated_user_can_update(self):
        """Test that authenticated users can update books."""
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated by Auth User',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = self.authenticated_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authenticated_user_can_delete(self):
        """Test that authenticated users can delete books."""
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = self.authenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookPaginationTests(BookAPITestCase):
    """Tests for pagination functionality."""
    
    def test_pagination_structure(self):
        """Test that paginated response has correct structure."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
    
    def test_pagination_count(self):
        """Test that pagination count is correct."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.data['count'], 4)


class BookValidationTests(BookAPITestCase):
    """Tests for data validation."""
    
    def test_publication_year_validation_current_year(self):
        """Test that current year is valid."""
        current_year = datetime.now().year
        data = {
            'title': 'Current Year Book',
            'publication_year': current_year,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_publication_year_validation_past_year(self):
        """Test that past years are valid."""
        data = {
            'title': 'Old Book',
            'publication_year': 1990,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_publication_year_validation_future_year(self):
        """Test that future years are rejected."""
        future_year = datetime.now().year + 10
        data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
    
    def test_required_fields_validation(self):
        """Test that all required fields are validated."""
        # Missing title
        data = {
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.authenticated_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)


class BookAuthenticationTests(BookAPITestCase):
    """Tests for authentication using client.login() method."""
    
    def test_login_and_create_book(self):
        """Test creating a book after logging in with client.login()."""
        # Create a new client and login
        client = APIClient()
        login_successful = client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful)
        
        # Attempt to create a book
        data = {
            'title': 'Book Created After Login',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Book Created After Login')
    
    def test_login_and_update_book(self):
        """Test updating a book after logging in with client.login()."""
        client = APIClient()
        login_successful = client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful)
        
        url = reverse('book-update', kwargs={'pk': self.book1.pk})
        data = {
            'title': 'Updated After Login',
            'publication_year': 2020,
            'author': self.author1.pk
        }
        response = client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated After Login')
    
    def test_login_and_delete_book(self):
        """Test deleting a book after logging in with client.login()."""
        client = APIClient()
        login_successful = client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful)
        
        url = reverse('book-delete', kwargs={'pk': self.book1.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book1.pk).exists())
    
    def test_login_failure_with_wrong_credentials(self):
        """Test that login fails with incorrect credentials."""
        client = APIClient()
        login_successful = client.login(username='testuser', password='wrongpassword')
        self.assertFalse(login_successful)
        
        # Verify that requests requiring authentication still fail
        data = {
            'title': 'Should Fail',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_logout_revokes_access(self):
        """Test that logging out revokes authenticated access."""
        client = APIClient()
        client.login(username='testuser', password='testpass123')
        
        # Verify authenticated access works
        data = {
            'title': 'Before Logout',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Logout
        client.logout()
        
        # Verify access is revoked after logout
        data = {
            'title': 'After Logout',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_logged_in_client_can_perform_crud(self):
        """Test that the logged-in client from setUp can perform CRUD operations."""
        # Test Create
        data = {
            'title': 'CRUD Test Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = self.logged_in_client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book_id = response.data['id']
        
        # Test Read
        url = reverse('book-detail', kwargs={'pk': book_id})
        response = self.logged_in_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test Update
        url = reverse('book-update', kwargs={'pk': book_id})
        data['title'] = 'Updated CRUD Test Book'
        response = self.logged_in_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test Delete
        url = reverse('book-delete', kwargs={'pk': book_id})
        response = self.logged_in_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_admin_user_login(self):
        """Test that admin users can login and perform operations."""
        client = APIClient()
        login_successful = client.login(username='adminuser', password='adminpass123')
        self.assertTrue(login_successful)
        
        # Admin should be able to create books
        data = {
            'title': 'Admin Created Book',
            'publication_year': 2023,
            'author': self.author1.pk
        }
        response = client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
