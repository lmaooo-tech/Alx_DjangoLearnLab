"""
URL Configuration for the API application.

This module defines all URL patterns for the Book and Author model API endpoints,
mapping URLs to their corresponding views for CRUD operations.

Book Endpoints:
- /api/books/                 - List all books (GET) with filtering, search, ordering
- /api/books/create/          - Create new book (POST)
- /api/books/<int:pk>/        - Retrieve specific book (GET)
- /api/books/<int:pk>/update/ - Update book (PUT/PATCH)
- /api/books/<int:pk>/delete/ - Delete book (DELETE)

Author Endpoints:
- /api/authors/                 - List all authors (GET) with search, ordering
- /api/authors/create/          - Create new author (POST)
- /api/authors/<int:pk>/        - Retrieve specific author (GET)
- /api/authors/<int:pk>/update/ - Update author (PUT/PATCH)
- /api/authors/<int:pk>/delete/ - Delete author (DELETE)
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # ========================================================================
    # BOOK ENDPOINTS - STEP 4 INTEGRATION
    # ========================================================================
    # Full filtering, searching, ordering on BookListView
    # ========================================================================
    
    # Book List and Create Endpoints
    # GET:  Retrieve paginated list with filters, search, ordering
    # POST: Create a new book
    path('books/', views.BookListView.as_view(), name='book-list'),
    
    # Book Create Endpoint (Alternative POST endpoint)
    # POST: Create a new book with explicit route
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # Book Detail Endpoint
    # GET: Retrieve a specific book by its ID
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Book Update Endpoint
    # PUT:  Full update of a specific book (all fields required)
    # PATCH: Partial update of a specific book (only specified fields)
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    
    # Book Delete Endpoint
    # DELETE: Remove a specific book by its ID
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    
    # ========================================================================
    # AUTHOR ENDPOINTS - STEP 4 INTEGRATION DEMONSTRATION
    # ========================================================================
    # Search and ordering on AuthorListView
    # Demonstrates integration patterns applied to different model
    # ========================================================================
    
    # Author List Endpoint
    # GET:  Retrieve paginated list of authors with search and ordering
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    
    # Author Create Endpoint
    # POST: Create a new author
    path('authors/create/', views.AuthorCreateView.as_view(), name='author-create'),
    
    # Author Detail Endpoint
    # GET: Retrieve a specific author and their books
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # Author Update Endpoint
    # PUT:  Full update of author (all fields required)
    # PATCH: Partial update of author (only specified fields)
    path('authors/<int:pk>/update/', views.AuthorUpdateView.as_view(), name='author-update'),
    
    # Author Delete Endpoint
    # DELETE: Remove a specific author
    path('authors/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author-delete'),
]

