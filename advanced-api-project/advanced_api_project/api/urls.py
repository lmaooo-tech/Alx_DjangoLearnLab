"""
URL Configuration for the API application.

This module defines all URL patterns for the Book model API endpoints,
mapping URLs to their corresponding views for CRUD operations.

Endpoints:
- /api/books/                 - List all books (GET) & Create new book (POST)
- /api/books/<int:pk>/        - Retrieve, update, or delete a specific book
- /api/books/<int:pk>/update/ - Update a specific book (PUT/PATCH)
- /api/books/<int:pk>/delete/ - Delete a specific book (DELETE)
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # ========================================================================
    # Book List and Create Endpoints
    # ========================================================================
    # GET:  Retrieve a paginated list of all books
    # POST: Create a new book
    path('books/', views.BookListView.as_view(), name='book-list'),
    
    # ========================================================================
    # Book Create Endpoint (Alternative POST endpoint)
    # ========================================================================
    # POST: Create a new book with explicit route
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # ========================================================================
    # Book Detail Endpoint
    # ========================================================================
    # GET: Retrieve a specific book by its ID
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # ========================================================================
    # Book Update Endpoint
    # ========================================================================
    # PUT:  Full update of a specific book (all fields required)
    # PATCH: Partial update of a specific book (only specified fields)
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    
    # ========================================================================
    # Book Delete Endpoint
    # ========================================================================
    # DELETE: Remove a specific book by its ID
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
]
