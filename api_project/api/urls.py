from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import BookList, BookViewSet

# Create a router and register the BookViewSet
# DefaultRouter automatically creates URL patterns for all CRUD operations
router = DefaultRouter()
router.register(r'books_all', BookViewSet, basename='book_all')

urlpatterns = [
    # Route for the BookList view (ListAPIView)
    # GET /api/books/ - List all books (requires authentication)
    path('books/', BookList.as_view(), name='book-list'),

    # Token authentication endpoint
    # POST /api/auth/token/ - Obtain authentication token
    # Request body: {"username": "user", "password": "pass"}
    # Response: {"token": "<token_key>"}
    # Use this token in subsequent requests: Authorization: Token <token_key>
    path('auth/token/', obtain_auth_token, name='api-token-auth'),

    # Include the router URLs for BookViewSet (all CRUD operations)
    # GET /api/books_all/ - List all books
    # POST /api/books_all/ - Create a new book
    # GET /api/books_all/<id>/ - Retrieve a specific book
    # PUT /api/books_all/<id>/ - Update a book
    # PATCH /api/books_all/<id>/ - Partially update a book
    # DELETE /api/books_all/<id>/ - Delete a book
    # All endpoints require authentication (Token in Authorization header)
    path('', include(router.urls)),  # This includes all routes registered with the router
]
