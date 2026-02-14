from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView
)

urlpatterns = [
    # List all books
    path('books/', BookListView.as_view(), name='book-list'),
    
    # Retrieve a single book by ID
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    
    # Create a new book
    path('books/create/', BookCreateView.as_view(), name='book-create'),
    
    # Update an existing book (with explicit update suffix)
    path('books/update/<int:pk>/', BookUpdateView.as_view(), name='book-update'),
    
    # Delete a book (with explicit delete suffix)
    path('books/delete/<int:pk>/', BookDeleteView.as_view(), name='book-delete'),
]
