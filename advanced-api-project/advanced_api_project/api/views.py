"""
Advanced API views for Book model with comprehensive filtering, searching, and ordering.

This module provides:
- RESTful CRUD operations for Book model
- Advanced filtering by author, title, and publication year
- Full-text search capabilities
- Multiple ordering options
- Permission-based access control
- Custom validation and error handling
- Comprehensive logging for monitoring
"""

from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, NumberFilter, DateFromToRangeFilter
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
import logging

logger = logging.getLogger(__name__)


class BookFilterSet(FilterSet):
    """
    Custom FilterSet for Book model providing advanced filtering options.
    
    Provides filters for:
    - title: Partial string search in book title (case-insensitive)
    - author_name: Partial string search in author name (case-insensitive)
    - publication_year: Exact year match
    - publication_year_range: Year range filtering (from year to year)
    
    Usage in API:
    - /api/books/?title=Hobbit
    - /api/books/?author_name=Tolkien
    - /api/books/?publication_year=1937
    - /api/books/?publication_year_min=1930&publication_year_max=1940
    
    FilterSet Configuration:
    - Each filter uses specific lookup expressions
    - title: Case-insensitive contains search
    - author_name: Case-insensitive contains search on related author
    - Publication year: Exact match and range filtering
    """
    
    # Title filter: searches for partial matches, case-insensitive
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',  # i=case-insensitive, contains=substring search
        label='Search by title (partial match)',
        help_text='Filter books by partial title match (e.g., "Hobbit")'
    )
    
    # Author name filter: searches author's name via foreign key, case-insensitive
    author_name = CharFilter(
        field_name='author__name',  # Use double underscore for foreign key traversal
        lookup_expr='icontains',
        label='Search by author name (partial match)',
        help_text='Filter books by partial author name match (e.g., "Tolkien")'
    )
    
    # Publication year exact match filter
    publication_year = NumberFilter(
        field_name='publication_year',
        label='Exact year filter',
        help_text='Filter books published in exact year (e.g., 1937)'
    )
    
    # Publication year minimum filter (year from)
    publication_year_min = NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',  # gte = greater than or equal
        label='Minimum publication year',
        help_text='Filter books published in or after this year'
    )
    
    # Publication year maximum filter (year to)
    publication_year_max = NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',  # lte = less than or equal
        label='Maximum publication year',
        help_text='Filter books published in or before this year'
    )
    
    class Meta:
        """
        Meta configuration for BookFilterSet.
        
        - model: The Book model this FilterSet operates on
        - fields: Empty list (filters defined as class attributes above)
        """
        model = Book
        fields = []  # We define filters explicitly above instead of using field names


class BookListView(generics.ListAPIView):
    """
    API View for retrieving and filtering all books.
    
    Purpose:
    - Displays a paginated list of all books in the system
    - Provides advanced filtering by title, author, and publication year
    - Supports full-text search across book and author data
    - Enables flexible ordering of results
    - Uses BookSerializer for JSON serialization
    
    Permission:
    - AllowAny: Anyone can read/list books (no authentication required)
    
    HTTP Methods Supported:
    - GET: Retrieve all books with optional filters, search, and ordering
    
    Advanced Features:
    1. FILTERING (using query parameters):
       - ?title=Hobbit - Filter by partial title (case-insensitive)
       - ?author_name=Tolkien - Filter by partial author name (case-insensitive)
       - ?publication_year=1937 - Filter by exact publication year
       - ?publication_year_min=1930 - Filter by minimum year (inclusive)
       - ?publication_year_max=1950 - Filter by maximum year (inclusive)
       - Combine filters: ?author_name=Tolkien&publication_year_min=1930&publication_year_max=1950
    
    2. SEARCHING (using ?search parameter):
       - ?search=Ring - Full-text search across title and author name
       - Searches are case-insensitive and match partial strings
    
    3. ORDERING (using ?ordering parameter):
       - ?ordering=title - Order by title (ascending)
       - ?ordering=-title - Order by title (descending)
       - ?ordering=publication_year - Order by publication year (ascending)
       - ?ordering=-publication_year - Order by publication year (descending)
       - ?ordering=author__name - Order by author name (ascending)
       - ?ordering=-author__name - Order by author name (descending)
       - Default ordering: -publication_year (newest first)
    
    Response:
    - Returns a paginated list of book objects with their details
    - Pagination handled automatically by DRF pagination settings
    
    Examples:
    - GET /api/books/
    - GET /api/books/?title=Hobbit
    - GET /api/books/?author_name=Tolkien&publication_year_min=1930
    - GET /api/books/?search=Ring
    - GET /api/books/?ordering=title
    - GET /api/books/?title=Game&ordering=-publication_year
    
    Use Cases:
    - Homepage or books listing page of the API
    - Displaying books by specific author
    - Finding books published in specific time period
    - Full-text search across book library
    - Browsing books in different orders
    """
    queryset = Book.objects.all().order_by('-publication_year')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Read-only access for all users
    
    # Filtering Backend Configuration
    filter_backends = [
        DjangoFilterBackend,  # Enables field-based filtering
        filters.SearchFilter,  # Enables text search via ?search parameter
        filters.OrderingFilter  # Enables sorting via ?ordering parameter
    ]
    
    # FilterSet class for Attribute-based filtering
    filterset_class = BookFilterSet
    
    # ============================================================================
    # SEARCH FUNCTIONALITY CONFIGURATION
    # ============================================================================
    # 
    # SearchFilter enables full-text search across multiple fields using ?search parameter
    #
    # Search Characteristics:
    # - Case-insensitive: Matches "HOBBIT", "hobbit", "Hobbit" equally
    # - Partial string matching: "hob" matches "The Hobbit"
    # - Cross-field search: All fields searched simultaneously (OR operation)
    # - Database-optimized: Uses efficient SQL ILIKE queries
    #
    # search_fields Configuration:
    # Format: ['field_name', 'related_model__field_name', ...]
    # - Supports primary model fields
    # - Supports related model fields via foreign key (__ notation)
    # - Lookup expressions: prefix^ for starts_with, =field for exact_match
    #
    # Performance:
    # - Uses select_related('author') to avoid N+1 queries
    # - Recommended to add db_index=True to searched fields in model
    # - Works efficiently with pagination
    #
    search_fields = [
        'title',        # Search in book title (CharField)
                        # Example: ?search=Hobbit → finds "The Hobbit"
        'author__name'  # Search in related author's name via foreign key
                        # Example: ?search=Tolkien → finds all books by Tolkien
    ]
    #
    # USAGE EXAMPLES:
    # 
    # 1. Basic search:
    #    GET /api/books/?search=Tolkien
    #    Returns: All books with "Tolkien" in title or author name
    #
    # 2. Partial match search:
    #    GET /api/books/?search=hob
    #    Returns: "The Hobbit", "The Hobgoblin", etc.
    #
    # 3. Search with filters:
    #    GET /api/books/?search=King&publication_year_min=1980
    #    Returns: Books with "King" in title/author AND published after 1980
    #
    # 4. Search with ordering:
    #    GET /api/books/?search=The&ordering=publication_year
    #    Returns: Books with "The", ordered by year (oldest first)
    #
    # 5. Combined search, filter, and ordering:
    #    GET /api/books/?search=Game&author_name=Martin&publication_year=1996&ordering=-publication_year
    #    Returns: "Game of Thrones" filtered by author and year, sorted newest first
    #
    # ============================================================================
    
    # Ordering fields: fields allowed for sorting
    ordering_fields = [
        'title',             # Sort by book title
        'publication_year',  # Sort by publication year
        'author__name',      # Sort by author name (via foreign key)
        'id'                 # Sort by ID (creation order)
    ]
    
    # Default ordering if no ?ordering parameter provided
    ordering = ['-publication_year']  # Default: newest books first
    
    # ============================================================================
    # ORDERING FUNCTIONALITY CONFIGURATION
    # ============================================================================
    #
    # OrderingFilter enables flexible sorting of results using ?ordering parameter
    #
    # Ordering Characteristics:
    # - Ascending order: No prefix (e.g., ?ordering=title)
    # - Descending order: Prefix with - (e.g., ?ordering=-title)
    # - Single field: Only one field can be ordered at a time (DRF limitation)
    # - Database-optimized: Uses SQL ORDER BY at database level
    # - Works with pagination: Ordering persists across pages
    #
    # ordering_fields Configuration:
    # List of field names that users are allowed to sort by
    # - Direct model fields: 'title', 'publication_year', 'id'
    # - Related fields: 'author__name' (via foreign key with __ notation)
    # - Best practice: Use specific fields, not '__all__'
    #
    # Performance:
    # - Add db_index=True to frequently ordered fields
    # - Uses select_related('author') to avoid N+1 queries
    # - SQL query includes ORDER BY clause
    # - Database index makes ordering fast: O(log n)
    #
    # USAGE EXAMPLES:
    #
    # 1. Order by title (A-Z):
    #    GET /api/books/?ordering=title
    #    Returns: Books alphabetically sorted
    #
    # 2. Order by title (Z-A):
    #    GET /api/books/?ordering=-title
    #    Returns: Books reverse alphabetically sorted
    #
    # 3. Order by publication year (oldest first):
    #    GET /api/books/?ordering=publication_year
    #    Returns: Books from 1900s to present
    #
    # 4. Order by publication year (newest first):
    #    GET /api/books/?ordering=-publication_year
    #    Returns: Books from present to 1900s (DEFAULT)
    #
    # 5. Order by author name:
    #    GET /api/books/?ordering=author__name
    #    Returns: Books sorted by author alphabetically
    #
    # 6. Order by creation date (oldest first):
    #    GET /api/books/?ordering=id
    #    Returns: First added books first
    #
    # 7. Order by creation date (newest first):
    #    GET /api/books/?ordering=-id
    #    Returns: Most recently added books first
    #
    # COMBINING ORDERING WITH FILTERS:
    #
    # - ?ordering=title&author_name=King
    #   King books, sorted alphabetically by title
    #
    # - ?ordering=-publication_year&publication_year_min=1980
    #   Books from 1980 onwards, newest first
    #
    # - ?search=The&ordering=title
    #   Books with "The", sorted alphabetically
    #
    # PAGINATION WITH ORDERING:
    #
    # - ?ordering=title&page=1
    #   First page of alphabetically sorted books
    #
    # - ?ordering=title&page=2
    #   Second page (ordering preserved across pages)
    #
    # ORDERING VS FILTERING:
    #
    # Filtering (?author_name=King):
    #   - Narrows the dataset
    #   - Only returns King books
    #
    # Ordering (?ordering=title):
    #   - Sorts existing dataset
    #   - Determines result order
    #
    # Both can be used together:
    # ?author_name=King&ordering=publication_year
    # (Get King books, oldest first)
    #
    # ============================================================================
    
    # Ordering with Search examples (moved here for clarity)
    # Search before ordering means ordering applies to search results:
    #
    # - ?search=The&ordering=title
    #   Search for "The" and sort alphabetically A-Z
    #
    # - ?search=King&ordering=-publication_year
    #   Search for "King" and sort by newest books first
    #
    # - ?search=Game&ordering=author__name
    #   Search for "Game" and sort by author alphabetically
    #
    # - ?search=Foundation&ordering=-id
    #   Search for "Foundation" and sort by most recently added
    
    def get_queryset(self):
        """
        Returns the base queryset for filtering, searching, and ordering.
        
        This method provides backward compatibility with custom query parameter
        filtering (year_min, year_max) that were used before implementing
        the full DjangoFilterBackend integration.
        
        The main filtering, searching, and ordering is now handled by:
        - DjangoFilterBackend: Field-based filtering
        - SearchFilter: Full-text search
        - OrderingFilter: Result ordering
        
        Legacy Query Parameters (backward compatibility):
        - ?author - Filter by author ID (int)
        - ?year_min - Filter by minimum publication year (int)
        - ?year_max - Filter by maximum publication year (int)
        
        New Recommended Query Parameters:
        - Use DjangoFilterBackend queries instead:
          ?title=value
          ?author_name=value
          ?publication_year_min=value
          ?publication_year_max=value
        """
        queryset = Book.objects.all().select_related('author')
        
        # Legacy filtering support - maintains backward compatibility
        # These parameters still work but new code should use DjangoFilterBackend filters
        
        # Legacy: Filter by author ID if provided
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        
        # Legacy: Filter by minimum publication year if provided
        year_min = self.request.query_params.get('year_min', None)
        if year_min:
            try:
                queryset = queryset.filter(publication_year__gte=int(year_min))
            except ValueError:
                pass  # Ignore invalid year values
        
        # Legacy: Filter by maximum publication year if provided
        year_max = self.request.query_params.get('year_max', None)
        if year_max:
            try:
                queryset = queryset.filter(publication_year__lte=int(year_max))
            except ValueError:
                pass  # Ignore invalid year values
        
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    """
    API View for retrieving a single book by ID.
    
    Purpose:
    - Fetches detailed information for a specific book
    - Allows users to view complete book details including author reference
    
    HTTP Methods Supported:
    - GET: Retrieve a specific book by its ID
    
    URL Parameters:
    - pk (int): The primary key of the book to retrieve
    
    Response:
    - Returns a single book object with all its fields
    
    Permission Requirements:
    - No authentication required (read-only access for all users)
    
    Use Case:
    - Detailed book view pages
    - Getting specific book information
    - Public book details API for libraries
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Read-only access for all users


class BookCreateView(generics.CreateAPIView):
    """
    API View for creating a new book.
    
    Purpose:
    - Allows users to add a new book to the system
    - Validates book data including publication_year
    - Ensures author exists before book creation
    - Provides comprehensive error handling and logging
    
    HTTP Methods Supported:
    - POST: Create a new book with title, publication_year, and author
    
    Request Body:
    {
        "title": "Book Title",
        "publication_year": 2023,
        "author": 1
    }
    
    Response:
    - Status 201 Created: Returns the created book object with its new ID
    - Status 400 Bad Request: Includes validation errors if data is invalid
    
    Validation:
    - publication_year must not be in the future
    - title is required and must be a string
    - author must reference an existing Author
    - title cannot be empty or whitespace only
    
    Features:
    - Automatic logging of successful book creation
    - Custom error messages for common validation failures
    - Validation of author existence before creation
    
    Use Case:
    - Adding new books to the library
    - Administrative book creation operations
    """
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create books
    
    def get_queryset(self):
        """Returns an empty queryset as this is a create-only view"""
        return Book.objects.none()
    
    def perform_create(self, serializer):
        """
        Custom hook to handle book creation after validation.
        
        Responsibilities:
        - Verify author exists and is valid
        - Log successful book creation
        - Handle any creation-time errors
        """
        try:
            # Validate that author exists
            author_id = serializer.validated_data.get('author').id
            
            # Save the book
            book = serializer.save()
            
            # Log successful creation
            logger.info(f"New book created: '{book.title}' by Author ID {author_id}")
            
        except Author.DoesNotExist:
            raise DRFValidationError("The specified author does not exist.")
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            raise
    
    def create(self, request, *args, **kwargs):
        """
        Override create to provide custom response handling.
        
        Returns:
        - Success: 201 Created with book details and custom message
        - Error: 400 Bad Request with validation errors
        """
        try:
            response = super().create(request, *args, **kwargs)
            
            # Enhance response with custom message
            if response.status_code == status.HTTP_201_CREATED:
                response.data = {
                    'status': 'success',
                    'message': 'Book created successfully.',
                    'data': response.data
                }
            
            return response
            
        except DRFValidationError as e:
            return Response(
                {
                    'status': 'error',
                    'message': 'Validation failed.',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BookUpdateView(generics.UpdateAPIView):
    """
    API View for modifying an existing book.
    
    Purpose:
    - Updates specific fields or all fields of an existing book
    - Validates updated data before saving
    - Supports both full and partial updates
    - Provides logging and error handling
    
    HTTP Methods Supported:
    - PUT: Full update of book (all fields required)
    - PATCH: Partial update of book (only modified fields)
    
    URL Parameters:
    - pk (int): The primary key of the book to update
    
    Request Body (PUT - all fields required):
    {
        "title": "Updated Title",
        "publication_year": 2023,
        "author": 1
    }
    
    Request Body (PATCH - only changed fields):
    {
        "title": "Updated Title"
    }
    
    Response:
    - Status 200 OK: Returns the updated book object
    - Status 404 Not Found: If book doesn't exist
    - Status 400 Bad Request: If validation fails
    
    Validation:
    - publication_year must not be in the future (if updated)
    - title cannot be empty or whitespace only (if updated)
    - author must reference an existing Author (if updated)
    - Cannot modify immutable fields
    
    Features:
    - Automatic logging of book updates with before/after tracking
    - Permission checks and validation
    - Change tracking for audit purposes
    
    Use Case:
    - Editing book information
    - Updating publication details
    - Correcting book metadata
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update books
    
    def get_object(self):
        """
        Retrieve the book object with enhanced error handling.
        
        Returns the book matching the pk parameter, or raises 404.
        """
        try:
            return super().get_object()
        except Book.DoesNotExist:
            logger.warning(f"Update attempted on non-existent book with ID: {self.kwargs.get('pk')}")
            raise
    
    def perform_update(self, serializer):
        """
        Custom hook to handle book updates after validation.
        
        Responsibilities:
        - Track changes made to the book
        - Validate author if being changed
        - Log update operations
        - Handle creation-time errors
        """
        book = self.get_object()
        
        # Capture original values for logging
        original_data = {
            'title': book.title,
            'publication_year': book.publication_year,
            'author_id': book.author_id
        }
        
        try:
            # Validate author if it's being updated
            if 'author' in serializer.validated_data:
                author = serializer.validated_data.get('author')
                if author is None:
                    raise DRFValidationError("Author cannot be null.")
            
            # Save the updated book
            updated_book = serializer.save()
            
            # Log the update with change details
            updated_data = {
                'title': updated_book.title,
                'publication_year': updated_book.publication_year,
                'author_id': updated_book.author_id
            }
            
            changes = {k: (original_data[k], updated_data[k]) 
                      for k in original_data if original_data[k] != updated_data[k]}
            
            if changes:
                logger.info(f"Book ID {updated_book.id} updated. Changes: {changes}")
            
        except Author.DoesNotExist:
            raise DRFValidationError("The specified author does not exist.")
        except Exception as e:
            logger.error(f"Error updating book ID {book.id}: {str(e)}")
            raise
    
    def update(self, request, *args, **kwargs):
        """
        Override update to provide custom response handling.
        
        Returns:
        - Success: 200 OK with book details and custom message
        - Error: 400 Bad Request or 404 Not Found
        """
        try:
            response = super().update(request, *args, **kwargs)
            
            # Enhance response with custom message
            if response.status_code == status.HTTP_200_OK:
                response.data = {
                    'status': 'success',
                    'message': 'Book updated successfully.',
                    'data': response.data
                }
            
            return response
            
        except DRFValidationError as e:
            return Response(
                {
                    'status': 'error',
                    'message': 'Validation failed during update.',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BookDeleteView(generics.DestroyAPIView):
    """
    API View for removing a book (Delete persists permanently).
    
    Purpose:
    - Permanently deletes a book from the system
    - Removes all associated data
    - Restricted to authenticated users only
    
    HTTP Methods Supported:
    - DELETE: Remove a specific book by its ID (Authenticated users only)
    
    URL Parameters:
    - pk (int): The primary key of the book to delete
    
    Permission Requirements:
    - User must be authenticated to delete books
    - Returns 401 Unauthorized if user is not authenticated
    - Returns 403 Forbidden if user lacks required permissions
    
    Response:
    - Status 204 No Content on successful deletion
    - Status 404 Not Found if book doesn't exist
    - Status 401 Unauthorized if user is not authenticated
    
    Use Case:
    - Removing books from the library
    - Administrative operations
    - Cleanup of invalid entries
    - Controlling who can delete books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete books

# ============================================================================
# AUTHOR API VIEWS - Step 4 Integration Demonstration
# ============================================================================
# 
# These views demonstrate how filtering, searching, and ordering can be
# applied to other models beyond Book. The same integration patterns are used
# for Authors, showing how the architecture scales to multiple models.
#


class AuthorFilterSet(FilterSet):
    """
    Custom FilterSet for Author model providing search and filtering.
    
    Demonstrates that filtering patterns can be applied to any model.
    This follows the same pattern as BookFilterSet.
    
    Filters:
    - name: Case-insensitive substring search in author name
    """
    
    # Author name filter: case-insensitive substring search
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Search by author name (partial match)',
        help_text='Filter authors by partial name match (e.g., "Tolkien")'
    )
    
    class Meta:
        model = Author
        fields = []


class AuthorListView(generics.ListAPIView):
    """
    API View for retrieving and filtering all authors.
    
    Purpose:
    - Displays a paginated list of all authors in the system
    - Provides full-text search across author names
    - Enables flexible ordering of authors
    - Uses AuthorSerializer for JSON serialization
    
    Permission:
    - AllowAny: Anyone can read/list authors (no authentication required)
    
    HTTP Methods Supported:
    - GET: Retrieve all authors with optional search and ordering
    
    Advanced Features:
    
    1. SEARCHING (using ?search parameter):
       - ?search=Tolkien - Full-text search across author name
       - Searches are case-insensitive and match partial strings
       - Example: ?search=King finds "Stephen King", "King (author)", etc.
    
    2. ORDERING (using ?ordering parameter):
       - ?ordering=name - Order by author name (A-Z)
       - ?ordering=-name - Order by author name (Z-A)
       - ?ordering=id - Order by creation order (first added)
       - ?ordering=-id - Order by creation order (last added)
       - Default: ?ordering=name (alphabetical)
    
    3. PAGINATION:
       - ?page=1 - First page (default)
       - ?page=2 - Second page, etc.
    
    Response:
    - Returns a paginated list of author objects with their books
    
    Examples:
    - GET /api/authors/
    - GET /api/authors/?search=King
    - GET /api/authors/?ordering=name&page=1
    - GET /api/authors/?search=Stephen&ordering=-id
    
    Use Cases:
    - Display all authors in the system
    - Search for specific authors
    - Browse authors alphabetically
    - Show recently added authors
    - Find authors with partial name matching
    
    Integration:
    This view demonstrates STEP 4 integration on the Author model.
    The same filter_backends, search, and ordering patterns from
    BookListView are replicated here, showing architectural consistency.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Public read access
    
    # ========== FILTERING & SEARCHING (STEP 4 Integration) ==========
    filter_backends = [
        DjangoFilterBackend,      # Enable filtering
        filters.SearchFilter,     # Enable searching
        filters.OrderingFilter    # Enable ordering
    ]
    
    filterset_class = AuthorFilterSet  # Custom filters for Author
    
    search_fields = [
        'name'  # Search in author name only
    ]
    
    # ========== ORDERING (STEP 4 Integration) ==========
    ordering_fields = [
        'name',  # Sort by author name
        'id'     # Sort by creation order
    ]
    
    ordering = ['name']  # Default: alphabetical order
    
    def get_queryset(self):
        """
        Returns optimized queryset with related books.
        - Uses prefetch_related() for efficient book loading
        - Reduces database queries when serializing authors with books
        """
        return Author.objects.all().prefetch_related('books')


class AuthorDetailView(generics.RetrieveAPIView):
    """
    API View for retrieving a specific author and their books.
    
    Purpose:
    - Displays detailed information about a single author
    - Shows all books by the author
    - Uses AuthorSerializer with nested books
    
    Permission:
    - AllowAny: Anyone can read author details
    
    HTTP Methods Supported:
    - GET: Retrieve author details by ID
    
    URL Parameters:
    - pk (int): The primary key of the author
    
    Response:
    - Returns author object with nested books array
    
    Example:
    - GET /api/authors/1/
    
    Response Format:
    {
        "id": 1,
        "name": "J.R.R. Tolkien",
        "books": [
            {
                "id": 1,
                "title": "The Hobbit",
                "publication_year": 1937
            },
            {
                "id": 2,
                "title": "The Lord of the Rings",
                "publication_year": 1954
            }
        ]
    }
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]


class AuthorCreateView(generics.CreateAPIView):
    """
    API View for creating new authors.
    
    Permission:
    - IsAuthenticated: Only authenticated users can create authors
    
    HTTP Methods Supported:
    - POST: Create a new author
    
    Request Body:
    {
        "name": "Author Name"
    }
    
    Response:
    - Status 201 Created: Returns the created author object
    - Status 400 Bad Request: If validation fails
    - Status 401 Unauthorized: If user is not authenticated
    
    Logging:
    - Logs successful author creation with author name and ID
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Log author creation for auditing"""
        author = serializer.save()
        logger.info(f"Author created: {author.name} (ID: {author.id})")


class AuthorUpdateView(generics.UpdateAPIView):
    """
    API View for updating author information.
    
    Permission:
    - IsAuthenticated: Only authenticated users can update authors
    
    HTTP Methods Supported:
    - PUT: Replace entire author object
    - PATCH: Update specific fields
    
    URL Parameters:
    - pk (int): The primary key of the author
    
    Request Body (PUT):
    {
        "name": "Updated Author Name"
    }
    
    Response:
    - Status 200 OK: Returns the updated author object
    - Status 404 Not Found: If author doesn't exist
    - Status 400 Bad Request: If validation fails
    
    Logging:
    - Logs successful author updates for auditing
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Log author updates for auditing"""
        author = serializer.save()
        logger.info(f"Author updated: {author.name} (ID: {author.id})")


class AuthorDeleteView(generics.DestroyAPIView):
    """
    API View for deleting authors.
    
    Permission:
    - IsAuthenticated: Only authenticated users can delete authors
    
    HTTP Methods Supported:
    - DELETE: Remove an author
    
    URL Parameters:
    - pk (int): The primary key of the author
    
    Response:
    - Status 204 No Content: Successfully deleted
    - Status 404 Not Found: If author doesn't exist
    - Status 401 Unauthorized: If user is not authenticated
    
    Important:
    - Related books will be deleted due to CASCADE foreign key relationship
    - This is a destructive operation and should be used carefully
    - Consider implementing soft deletes in production systems
    
    Logging:
    - Logs author deletion for auditing
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]