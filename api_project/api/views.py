from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Book
from .serializers import BookSerializer


class BookList(generics.ListAPIView):
    """
    API view to list all books.
    
    - Only authenticated users can access this endpoint
    - Requires token authentication via Authorization header
    - GET request returns a list of all books in JSON format
    
    Permission Classes:
    - IsAuthenticated: Ensures only authenticated users can access this view
      Unauthenticated requests will receive a 401 Unauthorized response
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Require authentication


class BookViewSet(viewsets.ModelViewSet):
    """
    API viewset for performing CRUD operations on Book model.
    
    This viewset automatically provides the following actions:
    - list: GET /api/books_all/ - List all books
    - create: POST /api/books_all/ - Create a new book
    - retrieve: GET /api/books_all/<id>/ - Get a specific book
    - update: PUT /api/books_all/<id>/ - Update a book (full update)
    - partial_update: PATCH /api/books_all/<id>/ - Partially update a book
    - destroy: DELETE /api/books_all/<id>/ - Delete a book
    
    Authentication:
    - All endpoints require token authentication
    - Include token in request header: Authorization: Token <token_key>
    - Obtain token by POSTing credentials to /api/auth/token/
    
    Permission Classes:
    - IsAuthenticated: All CRUD operations require authentication
      Unauthenticated requests will receive a 401 Unauthorized response
    
    Example usage:
    1. Get token: POST /api/auth/token/ with {"username": "user", "password": "pass"}
    2. Use token: Include "Authorization: Token <token_key>" in request headers
    3. Access API: GET, POST, PUT, PATCH, or DELETE to /api/books_all/ endpoints
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for all CRUD operations
