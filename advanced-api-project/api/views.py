from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter


# ListView - Retrieve all books
class BookListView(generics.ListAPIView):
    """
    API view to retrieve a list of all books with advanced query capabilities.
    
    ===================
    FILTERING OPTIONS:
    ===================
    - title: Filter by title (case-insensitive, contains)
      Example: /api/books/?title=django
    
    - author: Filter by author ID (exact match)
      Example: /api/books/?author=1
    
    - author_name: Filter by author name (case-insensitive, contains)
      Example: /api/books/?author_name=smith
    
    - publication_year: Filter by exact publication year
      Example: /api/books/?publication_year=2024
    
    - publication_year_min: Filter books published from this year onwards
      Example: /api/books/?publication_year_min=2020
    
    - publication_year_max: Filter books published up to this year
      Example: /api/books/?publication_year_max=2024
    
    - Combined range: /api/books/?publication_year_min=2020&publication_year_max=2024
    
    ===================
    SEARCH FUNCTIONALITY:
    ===================
    Use the 'search' parameter to perform text searches across multiple fields:
    - Searches in: title and author name
    - Case-insensitive partial matching
    
    Examples:
    - /api/books/?search=python - Find books with "python" in title or author name
    - /api/books/?search=django rest - Search for multiple terms
    
    ===================
    ORDERING OPTIONS:
    ===================
    Use the 'ordering' parameter to sort results:
    - Available fields: title, publication_year
    - Default order: title (ascending)
    - Use '-' prefix for descending order
    
    Examples:
    - /api/books/?ordering=title - Sort by title A-Z
    - /api/books/?ordering=-title - Sort by title Z-A
    - /api/books/?ordering=publication_year - Sort by year (oldest first)
    - /api/books/?ordering=-publication_year - Sort by year (newest first)
    
    ===================
    COMBINING QUERIES:
    ===================
    You can combine filtering, searching, and ordering:
    - /api/books/?author_name=smith&ordering=-publication_year
    - /api/books/?search=python&publication_year_min=2020&ordering=title
    
    ===================
    PAGINATION:
    ===================
    Results are paginated (10 items per page by default)
    - Use ?page=2 to access additional pages
    """
    queryset = Book.objects.all().select_related('author')  # Optimize queries
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read-only for unauthenticated users
    
    # Enable filtering, searching, and ordering backends
    filter_backends = [
        DjangoFilterBackend,  # For field-specific filtering
        filters.SearchFilter,  # For text search across multiple fields
        filters.OrderingFilter  # For sorting results
    ]
    
    # Advanced filtering using custom filter class
    filterset_class = BookFilter
    
    # Search configuration - enables text search across these fields
    search_fields = [
        'title',          # Search in book title
        'author__name'    # Search in related author's name
    ]
    
    # Ordering configuration - allows sorting by these fields
    ordering_fields = [
        'title',              # Allow ordering by title
        'publication_year'    # Allow ordering by publication year
    ]
    
    # Default ordering when no ordering parameter is provided
    ordering = ['title']


# DetailView - Retrieve a single book by ID
class BookDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a single book by its ID.
    """
    queryset = Book.objects.select_related('author')  # Optimize query with select_related
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# CreateView - Add a new book
class BookCreateView(generics.CreateAPIView):
    """
    API view to create a new book.
    Requires authentication.
    Includes custom validation and response handling.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create
    
    def perform_create(self, serializer):
        """
        Custom method to handle the creation of a new book.
        Can be extended to add custom logic like logging, notifications, etc.
        """
        # Save the book instance
        book = serializer.save()
        
        # Additional custom logic can be added here
        # For example: logging, sending notifications, etc.
        print(f"Book created: {book.title} by {book.author.name}")


# UpdateView - Modify an existing book
class BookUpdateView(generics.UpdateAPIView):
    """
    API view to update an existing book.
    Requires authentication.
    Supports both PUT (full update) and PATCH (partial update).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update
    
    def perform_update(self, serializer):
        """
        Custom method to handle the update of an existing book.
        Can be extended to add custom logic like audit trails, validation, etc.
        """
        # Get the instance being updated
        instance = self.get_object()
        old_title = instance.title
        
        # Save the updated book instance
        book = serializer.save()
        
        # Additional custom logic can be added here
        # For example: logging changes, audit trails, etc.
        print(f"Book updated: '{old_title}' -> '{book.title}'")


# DeleteView - Remove a book
class BookDeleteView(generics.DestroyAPIView):
    """
    API view to delete a book.
    Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete
    
    def perform_destroy(self, instance):
        """
        Custom method to handle the deletion of a book.
        Can be extended to add custom logic like soft deletes, logging, etc.
        """
        book_title = instance.title
        
        # Perform the deletion
        instance.delete()
        
        # Additional custom logic can be added here
        print(f"Book deleted: {book_title}")
