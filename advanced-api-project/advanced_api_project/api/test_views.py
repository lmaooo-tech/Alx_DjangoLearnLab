"""
Comprehensive Unit Tests for Book API Endpoints

Tests cover:
- CRUD operations (Create, Read, Update, Delete)
- Filtering functionality
- Searching functionality
- Ordering functionality
- Pagination
- Authentication and permissions
- Response data integrity
- Status code accuracy

Run tests with: python manage.py test api.tests.test_views -v 2
"""

from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.test import TestCase
from api.models import Book, Author
from api.serializers import BookSerializer, AuthorSerializer
import json


class BookCRUDTestCase(APITestCase):
    """
    Test CRUD (Create, Read, Update, Delete) operations for Book endpoints.
    """
    
    def setUp(self):
        """Set up test data and API client"""
        self.client = APIClient()
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create test author
        self.author = Author.objects.create(name="J.R.R. Tolkien")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.author
        )
        self.book2 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.author
        )
    
    # ===== READ TESTS =====
    
    def test_list_books(self):
        """Test retrieving list of all books"""
        response = self.client.get('/api/books/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn('count', data)
        self.assertIn('results', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        
        # Verify count
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['results']), 2)
    
    def test_list_books_response_format(self):
        """Test that list response has correct book format"""
        response = self.client.get('/api/books/')
        data = response.json()
        
        # Verify each book has required fields
        for book in data['results']:
            self.assertIn('id', book)
            self.assertIn('title', book)
            self.assertIn('publication_year', book)
            self.assertIn('author', book)
            
            # Verify data types
            self.assertIsInstance(book['id'], int)
            self.assertIsInstance(book['title'], str)
            self.assertIsInstance(book['publication_year'], int)
    
    def test_retrieve_single_book(self):
        """Test retrieving a single book by ID"""
        response = self.client.get(f'/api/books/{self.book1.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['id'], self.book1.id)
        self.assertEqual(data['title'], 'The Hobbit')
        self.assertEqual(data['publication_year'], 1937)
    
    def test_retrieve_nonexistent_book(self):
        """Test retrieving a book that doesn't exist"""
        response = self.client.get('/api/books/9999/')
        
        self.assertEqual(response.status_code, 404)
    
    # ===== CREATE TESTS =====
    
    def test_create_book_unauthenticated(self):
        """Test that unauthenticated users cannot create books"""
        data = {
            'title': 'New Book',
            'publication_year': 2025,
            'author': self.author.id
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_create_book_authenticated(self):
        """Test creating a book as authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'The Silmarillion',
            'publication_year': 1977,
            'author': self.author.id
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        # Verify book was created
        self.assertEqual(Book.objects.count(), 3)
        new_book = Book.objects.get(title='The Silmarillion')
        self.assertEqual(new_book.publication_year, 1977)
    
    def test_create_book_invalid_year(self):
        """Test that books with future publication year are rejected"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Future Book',
            'publication_year': 2099,  # Future year
            'author': self.author.id
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        # Should be rejected by validation
        self.assertEqual(response.status_code, 400)
    
    def test_create_book_missing_fields(self):
        """Test that required fields are enforced"""
        self.client.force_authenticate(user=self.user)
        
        # Missing title
        data = {
            'publication_year': 1977,
            'author': self.author.id
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
    
    # ===== UPDATE TESTS =====
    
    def test_update_book_unauthenticated(self):
        """Test that unauthenticated users cannot update books"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/books/{self.book1.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_update_book_authenticated(self):
        """Test updating a book as authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'The Hobbit: Updated',
            'publication_year': 1937
        }
        response = self.client.patch(f'/api/books/{self.book1.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify update was applied
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'The Hobbit: Updated')
    
    def test_put_update_book(self):
        """Test full update (PUT) of a book"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'The Hobbit',
            'publication_year': 1937,
            'author': self.author.id
        }
        response = self.client.put(f'/api/books/{self.book1.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['title'], 'The Hobbit')
    
    def test_update_nonexistent_book(self):
        """Test updating a book that doesn't exist"""
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Updated'}
        response = self.client.patch('/api/books/9999/update/', data, format='json')
        
        self.assertEqual(response.status_code, 404)
    
    # ===== DELETE TESTS =====
    
    def test_delete_book_unauthenticated(self):
        """Test that unauthenticated users cannot delete books"""
        response = self.client.delete(f'/api/books/{self.book1.id}/delete/')
        
        self.assertEqual(response.status_code, 401)
        
        # Verify book still exists
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_book_authenticated(self):
        """Test deleting a book as authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        book_id = self.book1.id
        response = self.client.delete(f'/api/books/{book_id}/delete/')
        
        self.assertEqual(response.status_code, 204)
        
        # Verify book was deleted
        self.assertFalse(Book.objects.filter(id=book_id).exists())
    
    def test_delete_nonexistent_book(self):
        """Test deleting a book that doesn't exist"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete('/api/books/9999/delete/')
        
        self.assertEqual(response.status_code, 404)


class BookFilteringTestCase(APITestCase):
    """
    Test filtering functionality on Book API.
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test authors
        self.tolkien = Author.objects.create(name="J.R.R. Tolkien")
        self.king = Author.objects.create(name="Stephen King")
        self.orwell = Author.objects.create(name="George Orwell")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.tolkien
        )
        self.book2 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.tolkien
        )
        self.book3 = Book.objects.create(
            title="The Shining",
            publication_year=1977,
            author=self.king
        )
        self.book4 = Book.objects.create(
            title="The Stand",
            publication_year=1978,
            author=self.king
        )
        self.book5 = Book.objects.create(
            title="1984",
            publication_year=1949,
            author=self.orwell
        )
    
    def test_filter_by_author_name(self):
        """Test filtering books by author name"""
        response = self.client.get('/api/books/?author_name=Tolkien')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        titles = [book['title'] for book in data['results']]
        self.assertIn('The Hobbit', titles)
        self.assertIn('The Lord of the Rings', titles)
    
    def test_filter_by_author_name_case_insensitive(self):
        """Test that author name filtering is case-insensitive"""
        response1 = self.client.get('/api/books/?author_name=tolkien')
        response2 = self.client.get('/api/books/?author_name=TOLKIEN')
        response3 = self.client.get('/api/books/?author_name=Tolkien')
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        self.assertEqual(data1['count'], data2['count'])
        self.assertEqual(data2['count'], data3['count'])
    
    def test_filter_by_title(self):
        """Test filtering books by title"""
        response = self.client.get('/api/books/?title=Hobbit')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'The Hobbit')
    
    def test_filter_by_publication_year_exact(self):
        """Test filtering by exact publication year"""
        response = self.client.get('/api/books/?publication_year=1978')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'The Stand')
    
    def test_filter_by_publication_year_min(self):
        """Test filtering by minimum publication year"""
        response = self.client.get('/api/books/?publication_year_min=1970')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return books from 1977 and 1978
        self.assertEqual(data['count'], 2)
        
        for book in data['results']:
            self.assertGreaterEqual(book['publication_year'], 1970)
    
    def test_filter_by_publication_year_max(self):
        """Test filtering by maximum publication year"""
        response = self.client.get('/api/books/?publication_year_max=1950')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return books from 1937, 1949
        self.assertEqual(data['count'], 2)
        
        for book in data['results']:
            self.assertLessEqual(book['publication_year'], 1950)
    
    def test_filter_by_year_range(self):
        """Test filtering by year range (both min and max)"""
        response = self.client.get('/api/books/?publication_year_min=1950&publication_year_max=1980')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return 1954, 1977, 1978
        self.assertEqual(data['count'], 3)
        
        for book in data['results']:
            self.assertGreaterEqual(book['publication_year'], 1950)
            self.assertLessEqual(book['publication_year'], 1980)
    
    def test_multiple_filters_combined(self):
        """Test combining multiple filters"""
        response = self.client.get('/api/books/?author_name=King&publication_year_min=1975')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should find King's books after 1975
        self.assertEqual(data['count'], 2)
        
        for book in data['results']:
            self.assertGreaterEqual(book['publication_year'], 1975)
    
    def test_filter_no_results(self):
        """Test filtering with no matching results"""
        response = self.client.get('/api/books/?author_name=NonExistent')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['results']), 0)


class BookSearchingTestCase(APITestCase):
    """
    Test searching functionality on Book API.
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.tolkien = Author.objects.create(name="J.R.R. Tolkien")
        self.king = Author.objects.create(name="Stephen King")
        
        self.book1 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.tolkien
        )
        self.book2 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.tolkien
        )
        self.book3 = Book.objects.create(
            title="The Shining",
            publication_year=1977,
            author=self.king
        )
        self.book4 = Book.objects.create(
            title="The Stand",
            publication_year=1978,
            author=self.king
        )
    
    def test_search_by_title(self):
        """Test searching for book by title"""
        response = self.client.get('/api/books/?search=Hobbit')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertGreater(data['count'], 0)
        self.assertIn('Hobbit', data['results'][0]['title'])
    
    def test_search_by_author_name(self):
        """Test searching for book by author name"""
        response = self.client.get('/api/books/?search=King')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should find both King books
        self.assertEqual(data['count'], 2)
    
    def test_search_case_insensitive(self):
        """Test that search is case-insensitive"""
        response1 = self.client.get('/api/books/?search=king')
        response2 = self.client.get('/api/books/?search=KING')
        response3 = self.client.get('/api/books/?search=King')
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        self.assertEqual(data1['count'], data2['count'])
        self.assertEqual(data2['count'], data3['count'])
    
    def test_search_partial_match(self):
        """Test searching with partial word"""
        response = self.client.get('/api/books/?search=ing')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # "ing" should match: Shining, Stand (endswith), and potentially others
        self.assertGreater(data['count'], 0)
    
    def test_search_no_results(self):
        """Test searching with no matching results"""
        response = self.client.get('/api/books/?search=NonexistentBook12345')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 0)
    
    def test_search_special_characters(self):
        """Test searching with special characters"""
        response = self.client.get('/api/books/?search=%27')  # Single quote URL encoded
        
        # Should not throw error, just return results or empty
        self.assertEqual(response.status_code, 200)
    
    def test_search_and_filter_together(self):
        """Test combining search with filter"""
        response = self.client.get('/api/books/?search=ing&author_name=King')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should find King books with "ing"
        for book in data['results']:
            self.assertIn('ing', book['title'].lower())


class BookOrderingTestCase(APITestCase):
    """
    Test ordering functionality on Book API.
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.tolkien = Author.objects.create(name="J.R.R. Tolkien")
        self.king = Author.objects.create(name="Stephen King")
        
        self.book1 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.tolkien
        )
        self.book2 = Book.objects.create(
            title="The Lord of the Rings",
            publication_year=1954,
            author=self.tolkien
        )
        self.book3 = Book.objects.create(
            title="The Shining",
            publication_year=1977,
            author=self.king
        )
        self.book4 = Book.objects.create(
            title="The Stand",
            publication_year=1978,
            author=self.king
        )
    
    def test_default_ordering(self):
        """Test that default ordering is newest first"""
        response = self.client.get('/api/books/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        years = [book['publication_year'] for book in data['results']]
        
        # Should be in descending order
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_ordering_by_title_ascending(self):
        """Test ordering by title (A-Z)"""
        response = self.client.get('/api/books/?ordering=title')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        titles = [book['title'] for book in data['results']]
        
        # Should be in alphabetical order
        self.assertEqual(titles, sorted(titles))
    
    def test_ordering_by_title_descending(self):
        """Test ordering by title (Z-A)"""
        response = self.client.get('/api/books/?ordering=-title')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        titles = [book['title'] for book in data['results']]
        
        # Should be in reverse alphabetical order
        self.assertEqual(titles, sorted(titles, reverse=True))
    
    def test_ordering_by_year_ascending(self):
        """Test ordering by publication year (oldest first)"""
        response = self.client.get('/api/books/?ordering=publication_year')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        years = [book['publication_year'] for book in data['results']]
        
        # Should be in ascending order
        self.assertEqual(years, sorted(years))
    
    def test_ordering_by_year_descending(self):
        """Test ordering by publication year (newest first)"""
        response = self.client.get('/api/books/?ordering=-publication_year')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        years = [book['publication_year'] for book in data['results']]
        
        # Should be in descending order
        self.assertEqual(years, sorted(years, reverse=True))
    
    def test_ordering_by_author_name(self):
        """Test ordering by foreign key (author name)"""
        response = self.client.get('/api/books/?ordering=author__name')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should not throw error
        self.assertGreater(len(data['results']), 0)
    
    def test_invalid_ordering_field(self):
        """Test that invalid ordering field returns error"""
        response = self.client.get('/api/books/?ordering=invalid_field')
        
        self.assertEqual(response.status_code, 400)
    
    def test_ordering_with_filter(self):
        """Test ordering works with filters"""
        response = self.client.get('/api/books/?author_name=King&ordering=title')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        titles = [book['title'] for book in data['results']]
        
        # Should be King's books in alphabetical order
        self.assertEqual(titles, sorted(titles))
        self.assertEqual(data['count'], 2)


class BookPaginationTestCase(APITestCase):
    """
    Test pagination functionality on Book API.
    """
    
    def setUp(self):
        """Set up test data with many books"""
        self.client = APIClient()
        
        author = Author.objects.create(name="Test Author")
        
        # Create 15 books to test pagination (default page size is 10)
        for i in range(15):
            Book.objects.create(
                title=f"Book {i+1}",
                publication_year=2000 + i,
                author=author
            )
    
    def test_pagination_page_1(self):
        """Test first page of pagination"""
        response = self.client.get('/api/books/?page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        
        # First page should have up to 10 items
        self.assertLessEqual(len(data['results']), 10)
        
        # Previous should be None on first page
        self.assertIsNone(data['previous'])
    
    def test_pagination_page_2(self):
        """Test second page of pagination"""
        response = self.client.get('/api/books/?page=2')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have pagination info
        self.assertIsNotNone(data['previous'])
    
    def test_pagination_count_accurate(self):
        """Test that count reflects total number of items"""
        response = self.client.get('/api/books/')
        data = response.json()
        
        # Created 15 books
        self.assertEqual(data['count'], 15)
    
    def test_pagination_with_filter(self):
        """Test that pagination works with filters"""
        # Add a different author with 5 books
        author2 = Author.objects.create(name="Different Author")
        for i in range(5):
            Book.objects.create(
                title=f"Different Book {i+1}",
                publication_year=2050 + i,
                author=author2
            )
        
        response = self.client.get('/api/books/?author_name=Different&page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 5)
    
    def test_pagination_with_ordering(self):
        """Test that pagination preserves ordering across pages"""
        response = self.client.get('/api/books/?ordering=title&page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        titles = [book['title'] for book in data['results']]
        
        # Should be ordered on page 1
        self.assertEqual(titles, sorted(titles))


class BookAuthenticationTestCase(APITestCase):
    """
    Test authentication and permission enforcement.
    """
    
    def setUp(self):
        """Set up test data and users"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=author
        )
    
    def test_read_without_authentication(self):
        """Test that reading books doesn't require authentication"""
        response = self.client.get('/api/books/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_create_without_authentication(self):
        """Test that creating requires authentication"""
        data = {
            'title': 'New Book',
            'publication_year': 2025,
            'author': 1
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_update_without_authentication(self):
        """Test that updating requires authentication"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/books/{self.book.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_delete_without_authentication(self):
        """Test that deleting requires authentication"""
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_create_with_authentication(self):
        """Test that authenticated user can create"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'New Book',
            'publication_year': 2025,
            'author': 1
        }
        response = self.client.post('/api/books/create/', data, format='json')
        
        # Should succeed or fail due to year validation, not auth
        self.assertIn(response.status_code, [201, 400])
    
    def test_update_with_authentication(self):
        """Test that authenticated user can update"""
        self.client.force_authenticate(user=self.user)
        
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/books/{self.book.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
    
    def test_delete_with_authentication(self):
        """Test that authenticated user can delete"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        
        self.assertEqual(response.status_code, 204)


class BookResponseDataIntegrityTestCase(APITestCase):
    """
    Test response data integrity and correctness.
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.author = Author.objects.create(
            name="Test Author",
            id=1
        )
        
        self.book = Book.objects.create(
            title="Test Book Title",
            publication_year=2020,
            author=self.author,
            id=1
        )
    
    def test_book_data_integrity(self):
        """Test that retrieved book data matches stored data"""
        response = self.client.get(f'/api/books/{self.book.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify exact values
        self.assertEqual(data['title'], 'Test Book Title')
        self.assertEqual(data['publication_year'], 2020)
        self.assertEqual(data['id'], self.book.id)
    
    def test_book_list_data_integrity(self):
        """Test that all books in list have correct data"""
        response = self.client.get('/api/books/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify we can find our book
        found = False
        for book in data['results']:
            if book['id'] == self.book.id:
                found = True
                self.assertEqual(book['title'], 'Test Book Title')
                self.assertEqual(book['publication_year'], 2020)
        
        self.assertTrue(found)
    
    def test_update_data_persistence(self):
        """Test that updated data is persisted correctly"""
        # Get user for authentication
        user = User.objects.create_user(username='testuser', password='test123')
        self.client.force_authenticate(user=user)
        
        # Update the book
        update_data = {
            'title': 'Updated Title',
            'publication_year': 2021,
            'author': self.author.id
        }
        response = self.client.put(f'/api/books/{self.book.id}/update/', update_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Retrieve the book again
        response = self.client.get(f'/api/books/{self.book.id}/')
        data = response.json()
        
        # Verify updated values are persisted
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['publication_year'], 2021)
    
    def test_filtered_results_accuracy(self):
        """Test that filtered results contain only matching items"""
        # Create additional books
        another_author = Author.objects.create(name="Another Author")
        Book.objects.create(
            title="Another Book",
            publication_year=2019,
            author=another_author
        )
        
        # Filter by author
        response = self.client.get(f'/api/books/?author_name={self.author.name}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should only have 1 result
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['id'], self.book.id)


class AuthorAPITestCase(APITestCase):
    """
    Test Author API endpoints (List, Detail, Create, Update, Delete).
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.author1 = Author.objects.create(name="Stephen King")
        self.author2 = Author.objects.create(name="J.R.R. Tolkien")
    
    def test_list_authors(self):
        """Test listing all authors"""
        response = self.client.get('/api/authors/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
    
    def test_retrieve_single_author(self):
        """Test retrieving a single author"""
        response = self.client.get(f'/api/authors/{self.author1.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['name'], 'Stephen King')
    
    def test_search_authors(self):
        """Test searching for authors"""
        response = self.client.get('/api/authors/?search=King')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'Stephen King')
    
    def test_order_authors(self):
        """Test ordering authors"""
        response = self.client.get('/api/authors/?ordering=name')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        names = [author['name'] for author in data['results']]
        
        # Should be in alphabetical order
        self.assertEqual(names, sorted(names))
    
    def test_create_author_authenticated(self):
        """Test creating an author"""
        self.client.force_authenticate(user=self.user)
        
        data = {'name': 'Isaac Asimov'}
        response = self.client.post('/api/authors/create/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Author.objects.count(), 3)
    
    def test_update_author_authenticated(self):
        """Test updating an author"""
        self.client.force_authenticate(user=self.user)
        
        data = {'name': 'S. King'}
        response = self.client.patch(f'/api/authors/{self.author1.id}/update/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.name, 'S. King')
    
    def test_delete_author_authenticated(self):
        """Test deleting an author (with cascade)"""
        self.client.force_authenticate(user=self.user)
        
        # Create a book under this author
        Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author1
        )
        
        author_id = self.author1.id
        response = self.client.delete(f'/api/authors/{author_id}/delete/')
        
        self.assertEqual(response.status_code, 204)
        
        # Author should be deleted
        self.assertFalse(Author.objects.filter(id=author_id).exists())


class APIEndpointStatusTestCase(APITestCase):
    """
    Test all endpoints respond with correct HTTP status codes.
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author
        )
    
    def test_get_books_list_status(self):
        """Test GET /api/books/ returns 200"""
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)
    
    def test_get_book_detail_status(self):
        """Test GET /api/books/{id}/ returns 200"""
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_get_nonexistent_book_status(self):
        """Test GET /api/books/{nonexistent}/ returns 404"""
        response = self.client.get('/api/books/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_post_without_auth_status(self):
        """Test POST without auth returns 401"""
        data = {'title': 'New', 'publication_year': 2025, 'author': self.author.id}
        response = self.client.post('/api/books/create/', data, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_post_with_auth_status(self):
        """Test POST with auth returns 201 or 400"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New', 'publication_year': 2025, 'author': self.author.id}
        response = self.client.post('/api/books/create/', data, format='json')
        self.assertIn(response.status_code, [201, 400])  # 400 if year validation fails
    
    def test_patch_without_auth_status(self):
        """Test PATCH without auth returns 401"""
        response = self.client.patch(f'/api/books/{self.book.id}/update/', {}, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_delete_without_auth_status(self):
        """Test DELETE without auth returns 401"""
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        self.assertEqual(response.status_code, 401)
    
    def test_delete_with_auth_status(self):
        """Test DELETE with auth returns 204"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/books/{self.book.id}/delete/')
        self.assertEqual(response.status_code, 204)
    
    def test_get_authors_list_status(self):
        """Test GET /api/authors/ returns 200"""
        response = self.client.get('/api/authors/')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_filter_status(self):
        """Test invalid filter returns 400"""
        response = self.client.get('/api/books/?ordering=nonexistent')
        self.assertEqual(response.status_code, 400)


class ComplexQueryTestCase(APITestCase):
    """
    Test complex queries combining multiple features.
    """
    
    def setUp(self):
        """Set up comprehensive test data"""
        self.client = APIClient()
        
        self.tolkien = Author.objects.create(name="J.R.R. Tolkien")
        self.king = Author.objects.create(name="Stephen King")
        
        Book.objects.create(title="The Hobbit", publication_year=1937, author=self.tolkien)
        Book.objects.create(title="The Lord of the Rings", publication_year=1954, author=self.tolkien)
        Book.objects.create(title="The Silmarillion", publication_year=1977, author=self.tolkien)
        Book.objects.create(title="The Shining", publication_year=1977, author=self.king)
        Book.objects.create(title="The Stand", publication_year=1978, author=self.king)
    
    def test_filter_search_order(self):
        """Test combining filter, search, and ordering"""
        response = self.client.get(
            '/api/books/?author_name=Tolkien&search=The&ordering=publication_year'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should find Tolkien books with "The", ordered by year
        self.assertGreater(data['count'], 0)
        
        years = [book['publication_year'] for book in data['results']]
        self.assertEqual(years, sorted(years))
    
    def test_year_range_filter_with_search(self):
        """Test year range filtering with search"""
        response = self.client.get(
            '/api/books/?publication_year_min=1970&publication_year_max=1980&search=ing'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify all results match criteria
        for book in data['results']:
            self.assertGreaterEqual(book['publication_year'], 1970)
            self.assertLessEqual(book['publication_year'], 1980)
    
    def test_pagination_with_multiple_filters(self):
        """Test pagination works correctly with filters"""
        # Create many books
        for i in range(15):
            Book.objects.create(
                title=f"King Book {i}",
                publication_year=2000 + i,
                author=self.king
            )
        
        response = self.client.get('/api/books/?author_name=King&page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertGreaterEqual(data['count'], 15)

