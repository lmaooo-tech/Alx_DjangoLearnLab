from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer


# ListView - Retrieve all books
class BookListView(generics.ListAPIView):
    """
    API view to retrieve a list of all books.
    Supports filtering by title, author, and publication year.
    Supports searching by title and author name.
    Supports ordering by title and publication_year.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read-only for unauthenticated users
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'author', 'publication_year']  # Fields that can be filtered
    search_fields = ['title', 'author__name']  # Fields that can be searched
    ordering_fields = ['title', 'publication_year']  # Fields that can be ordered
    ordering = ['title']  # Default ordering


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
