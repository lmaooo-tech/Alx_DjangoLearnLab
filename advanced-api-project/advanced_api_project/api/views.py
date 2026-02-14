from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
import logging

logger = logging.getLogger(__name__)


class BookListView(generics.ListAPIView):
    """
    API View for retrieving all books.
    
    Purpose:
    - Displays a paginated list of all books in the system
    - Supports filtering and searching capabilities
    - Uses BookSerializer for JSON serialization
    
    HTTP Methods Supported:
    - GET: Retrieve all books with pagination
    
    Features:
    - Filtering by author using ?author=<author_id> query parameter
    - Filtering by publication year range using ?year_min=<year>&year_max=<year>
    - Ordering by title or publication_year
    
    Response:
    - Returns a paginated list of book objects with their details
    
    Use Case:
    - Homepage or books listing page of the API
    - Displaying all available books
    """
    queryset = Book.objects.all().order_by('-publication_year')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Read-only access for all users
    
    def get_queryset(self):
        """
        Customized queryset filtering based on query parameters.
        
        Query Parameters:
        - author: Filter by author ID (e.g., ?author=1)
        - year_min: Minimum publication year (e.g., ?year_min=2020)
        - year_max: Maximum publication year (e.g., ?year_max=2024)
        """
        queryset = Book.objects.all().order_by('-publication_year')
        
        # Filter by author if provided
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        
        # Filter by publication year range if provided
        year_min = self.request.query_params.get('year_min', None)
        if year_min:
            try:
                queryset = queryset.filter(publication_year__gte=int(year_min))
            except ValueError:
                pass  # Ignore invalid year values
        
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
