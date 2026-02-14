# Book API Views Documentation

## Overview

This document provides detailed information about the Book API views, their configuration, and custom behavior. The API implements Django REST Framework generic views with custom hooks for enhanced functionality.

---

## Table of Contents

1. [Views Summary](#views-summary)
2. [View Configurations](#view-configurations)
3. [Custom Methods and Hooks](#custom-methods-and-hooks)
4. [Permission System](#permission-system)
5. [Filtering and Query Parameters](#filtering-and-query-parameters)
6. [Error Handling](#error-handling)
7. [Logging and Monitoring](#logging-and-monitoring)
8. [API Endpoints Reference](#api-endpoints-reference)

---

## Views Summary

The Book API consists of five main views that handle CRUD (Create, Read, Update, Delete) operations:

| View | HTTP Method | URL | Purpose |
|------|-------------|-----|---------|
| BookListView | GET | `/api/books/` | Retrieve paginated list of all books with filtering |
| BookDetailView | GET | `/api/books/<int:pk>/` | Retrieve details of a specific book |
| BookCreateView | POST | `/api/books/create/` | Create a new book (authenticated users only) |
| BookUpdateView | PUT, PATCH | `/api/books/<int:pk>/update/` | Update an existing book (authenticated users only) |
| BookDeleteView | DELETE | `/api/books/<int:pk>/delete/` | Delete a book (authenticated users only) |

---

## View Configurations

### 1. BookListView (ListAPIView)

**Base Class:** `generics.ListAPIView`

**Configuration:**
```python
queryset = Book.objects.all().order_by('-publication_year')
serializer_class = BookSerializer
permission_classes = [AllowAny]  # Read-only access for all users
```

**Custom Features:**
- Dynamic queryset filtering based on query parameters
- Support for multiple filtering options
- Automatic ordering by publication year (descending)

**Query Parameters Supported:**
- `author` (int): Filter books by author ID
- `year_min` (int): Minimum publication year
- `year_max` (int): Maximum publication year

**Example Requests:**
```bash
# Get all books
GET /api/books/

# Get books by author with ID 1
GET /api/books/?author=1

# Get books published between 1950 and 2000
GET /api/books/?year_min=1950&year_max=2000

# Combine filters
GET /api/books/?author=1&year_min=1950&year_max=2000
```

**Custom Method: `get_queryset()`**
- Overrides default queryset to add dynamic filtering
- Parses query parameters from request
- Handles invalid year values gracefully
- Returns filtered queryset ordered by publication year

---

### 2. BookDetailView (RetrieveAPIView)

**Base Class:** `generics.RetrieveAPIView`

**Configuration:**
```python
queryset = Book.objects.all()
serializer_class = BookSerializer
permission_classes = [AllowAny]  # Read-only access for all users
```

**Purpose:**
- Retrieve complete information for a single book
- Accessed via primary key (pk) in URL: `/api/books/<int:pk>/`
- Used for displaying detailed book information

**Example Request:**
```bash
GET /api/books/1/

Response (200 OK):
{
    "id": 1,
    "title": "The Shining",
    "publication_year": 1977,
    "author": 1
}
```

**Error Handling:**
- Returns 404 Not Found if book doesn't exist
- Returns 200 OK if book is found

---

### 3. BookCreateView (CreateAPIView)

**Base Class:** `generics.CreateAPIView`

**Configuration:**
```python
serializer_class = BookSerializer
permission_classes = [IsAuthenticated]  # Only authenticated users can create
```

**Purpose:**
- Allow authenticated users to create new books
- Enforces data validation before creation
- Logs successful book creation

**Permission Requirements:**
- User must be authenticated
- Returns 401 Unauthorized for unauthenticated requests

**Request Body:**
```json
{
    "title": "Book Title",
    "publication_year": 2023,
    "author": 1
}
```

**Custom Method: `get_queryset()`**
- Returns empty queryset (create-only view)
- Used internally for permission checks

**Custom Method: `perform_create(serializer)`**
- Called after validation but before save
- Validates author exists and is valid
- Logs successful book creation to logger
- Raises ValidationError if author doesn't exist

**Custom Method: `create(request, *args, **kwargs)`**
- Wraps the parent create method
- Enhances response with custom message
- Provides structured error responses
- Returns 201 Created on success
- Returns 400 Bad Request with detailed errors on failure

**Response Format - Success (201 Created):**
```json
{
    "status": "success",
    "message": "Book created successfully.",
    "data": {
        "id": 1,
        "title": "Book Title",
        "publication_year": 2023,
        "author": 1
    }
}
```

**Response Format - Error (400 Bad Request):**
```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": {
        "publication_year": ["Publication year cannot be in the future..."]
    }
}
```

**Validation Rules:**
- `title`: Required, must be a string
- `publication_year`: Required, must not be in the future, must be <= current year
- `author`: Required, must reference an existing Author

---

### 4. BookUpdateView (UpdateAPIView)

**Base Class:** `generics.UpdateAPIView`

**Configuration:**
```python
queryset = Book.objects.all()
serializer_class = BookSerializer
permission_classes = [IsAuthenticated]  # Only authenticated users can update
```

**Purpose:**
- Allow authenticated users to modify existing books
- Supports both full updates (PUT) and partial updates (PATCH)
- Tracks changes and logs update operations
- Validates all data before applying changes

**Permission Requirements:**
- User must be authenticated
- Returns 401 Unauthorized for unauthenticated requests

**HTTP Methods:**
- `PUT` (Full Update): All fields must be provided
- `PATCH` (Partial Update): Only changed fields are required

**Custom Method: `get_object()`**
- Retrieves the book matching the pk parameter
- Logs warning if book doesn't exist
- Raises 404 Not Found if book not found

**Custom Method: `perform_update(serializer)`**
- Called after validation but before save
- Captures original book values for change tracking
- Validates author if being updated
- Saves updated book to database
- Logs update with detailed change information
- Handles Author.DoesNotExist exception

**Custom Method: `update(request, *args, **kwargs)`**
- Wraps the parent update method
- Enhances response with custom message
- Provides structured error responses
- Returns 200 OK on success
- Returns 400 Bad Request with detailed errors on failure

**Response Format - Success (200 OK - PATCH):**
```json
{
    "status": "success",
    "message": "Book updated successfully.",
    "data": {
        "id": 1,
        "title": "Updated Title",
        "publication_year": 1977,
        "author": 1
    }
}
```

**Logging Example:**
```
Book ID 1 updated. Changes: {'title': ('Original Title', 'New Title')}
```

**Validation Rules:**
- Same as BookCreateView
- Only applied to fields being updated

---

### 5. BookDeleteView (DestroyAPIView)

**Base Class:** `generics.DestroyAPIView`

**Configuration:**
```python
queryset = Book.objects.all()
serializer_class = BookSerializer
permission_classes = [IsAuthenticated]  # Only authenticated users can delete
```

**Purpose:**
- Allow authenticated users to permanently delete books
- Removes book and all associated data from database
- Restricted to authenticated users only

**Permission Requirements:**
- User must be authenticated
- Returns 401 Unauthorized for unauthenticated requests

**Example Request:**
```bash
DELETE /api/books/1/delete/

Response (204 No Content):
(Empty body - indicates successful deletion)
```

**Response Codes:**
- 204 No Content: Book successfully deleted
- 404 Not Found: Book doesn't exist
- 401 Unauthorized: User not authenticated

---

## Custom Methods and Hooks

### Serializer Validation

The `BookSerializer` includes custom validation for the `publication_year` field:

```python
def validate_publication_year(self, value):
    """Validate that publication_year is not in the future"""
    current_year = datetime.now().year
    if value > current_year:
        raise serializers.ValidationError(
            f"Publication year cannot be in the future. Current year is {current_year}."
        )
    return value
```

This validation is applied to all write operations (Create and Update).

### Logging Integration

All views include logging capability through Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)
```

**Logged Events:**
- BookCreateView: `logger.info()` - Successful book creation
- BookCreateView: `logger.error()` - Creation errors
- BookUpdateView: `logger.warning()` - Update attempts on non-existent books
- BookUpdateView: `logger.info()` - Successful updates with change details
- BookUpdateView: `logger.error()` - Update errors

**Example Log Entry:**
```
INFO:api.views:New book created: 'The Hobbit' by Author ID 1
INFO:api.views:Book ID 5 updated. Changes: {'title': ('Original', 'Updated')}
WARNING:api.views:Update attempted on non-existent book with ID: 9999
ERROR:api.views:Error creating book: Author matching query does not exist.
```

---

## Permission System

### Permission Classes Configuration

**Read-Only Access (AllowAny):**
- `BookListView` - Anyone can list books
- `BookDetailView` - Anyone can view book details

**Authenticated-Only Access (IsAuthenticated):**
- `BookCreateView` - Only authenticated users can create
- `BookUpdateView` - Only authenticated users can update
- `BookDeleteView` - Only authenticated users can delete

### Authentication Methods Supported

DRF supports multiple authentication methods:

1. **Token Authentication**
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN_HERE" http://localhost:8000/api/books/create/ -X POST
   ```

2. **Session Authentication**
   - Login via Django admin or custom login endpoint
   - Cookies stored and automatically sent

3. **Basic Authentication**
   ```bash
   curl -u username:password http://localhost:8000/api/books/create/ -X POST
   ```

### Permission Error Responses

**401 Unauthorized:** User not authenticated
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:** User authenticated but lacks permissions
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

## Filtering and Query Parameters

### BookListView Filters

1. **Author Filter:**
   - Parameter: `author`
   - Type: Integer (Author ID)
   - Example: `?author=1`
   - Filters books by author

2. **Year Minimum Filter:**
   - Parameter: `year_min`
   - Type: Integer (Year)
   - Example: `?year_min=1950`
   - Returns books published in or after the year

3. **Year Maximum Filter:**
   - Parameter: `year_max`
   - Type: Integer (Year)
   - Example: `?year_max=2000`
   - Returns books published in or before the year

### Combined Filtering

```bash
# Get books by author 1 published between 1950 and 2000
GET /api/books/?author=1&year_min=1950&year_max=2000

# Get books published after 1980
GET /api/books/?year_min=1980

# Get books by author 2, any year
GET /api/books/?author=2
```

### Default Ordering

- Books are ordered by `publication_year` in descending order (newest first)
- Ordering is applied in `get_queryset()` method

---

## Error Handling

### Custom Error Format

All write operations (Create, Update) return structured error responses:

**Standard Validation Error:**
```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": {
        "field_name": ["Error message 1", "Error message 2"]
    }
}
```

**Example - Future Year Validation:**
```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": {
        "publication_year": ["Publication year cannot be in the future. Current year is 2026."]
    }
}
```

### Common HTTP Status Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 200 | OK | Successfully retrieved or updated resource |
| 201 | Created | Book successfully created |
| 204 | No Content | Book successfully deleted |
| 400 | Bad Request | Validation failed or malformed data |
| 401 | Unauthorized | User not authenticated for write operations |
| 403 | Forbidden | User lacks required permissions |
| 404 | Not Found | Resource doesn't exist |

---

## Logging and Monitoring

### Configure Logging

Add to `settings.py` to enable logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'api.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'api.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Monitoring Events

Track these key events in your logs:

1. **Book Creation**
   - Success: Book title, author ID, timestamp
   - Failure: Validation errors, missing fields

2. **Book Updates**
   - Success: Book ID, changes made, timestamp
   - Failure: Author not found, validation errors

3. **Failed Operations**
   - Unauthenticated access attempts to protected endpoints
   - Non-existent resource access attempts
   - Validation errors

---

## API Endpoints Reference

### Complete Endpoint List

```
# Read Endpoints (Public)
GET    /api/books/                    # List all books with filters
GET    /api/books/<int:pk>/           # Get single book details

# Write Endpoints (Authenticated Only)
POST   /api/books/                    # Create book (via list view)
POST   /api/books/create/             # Create book (explicit endpoint)
PUT    /api/books/<int:pk>/update/    # Full update book
PATCH  /api/books/<int:pk>/update/    # Partial update book
DELETE /api/books/<int:pk>/delete/    # Delete book
```

### Curl Examples

**List Books:**
```bash
curl http://localhost:8000/api/books/
```

**Get Single Book:**
```bash
curl http://localhost:8000/api/books/1/
```

**Create Book (Requires Authentication):**
```bash
curl -X POST http://localhost:8000/api/books/create/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Hobbit",
    "publication_year": 1937,
    "author": 1
  }'
```

**Update Book (Partial - Requires Authentication):**
```bash
curl -X PATCH http://localhost:8000/api/books/1/update/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

**Delete Book (Requires Authentication):**
```bash
curl -X DELETE http://localhost:8000/api/books/1/delete/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## Configuration Summary

### View Inheritance Chain

```
BookListView
└── ListAPIView
    ├── generics.GenericAPIView
    └── mixins.ListModelMixin

BookDetailView
└── RetrieveAPIView
    ├── generics.GenericAPIView
    └── mixins.RetrieveModelMixin

BookCreateView
└── CreateAPIView
    ├── generics.GenericAPIView
    └── mixins.CreateModelMixin

BookUpdateView
└── UpdateAPIView
    ├── generics.GenericAPIView
    └── mixins.UpdateModelMixin

BookDeleteView
└── DestroyAPIView
    ├── generics.GenericAPIView
    └── mixins.DestroyModelMixin
```

### Key Configuration Attributes

Each view is configured with:
- **queryset**: The database queryset to operate on
- **serializer_class**: The serializer to use for data transformation
- **permission_classes**: List of permission classes to enforce

### Settings Used from Django

- `REST_FRAMEWORK` settings in `settings.py`
- Pagination configuration
- Authentication configuration
- Default permission settings

---

## Testing

All views are thoroughly tested. Run tests with:

```bash
# Run all API tests
python manage.py test api

# Run specific view tests
python manage.py test api.tests.BookCreateViewTest

# Run with verbose output
python manage.py test api -v 2
```

See `tests.py` for comprehensive test coverage including:
- Permission enforcement
- CRUD operations
- Validation rules
- Error handling
- Integration tests

---

## Troubleshooting

### Issue: 401 Unauthorized on Write Operations

**Cause:** User not authenticated

**Solution:** 
- Provide valid authentication token in header: `Authorization: Token YOUR_TOKEN`
- Or login via session authentication first

### Issue: 400 Bad Request with Validation Error

**Cause:** Invalid data provided

**Solution:**
- Check error message in response for specific field errors
- Ensure `publication_year` is not in the future
- Ensure `author` ID exists in database

### Issue: 404 Not Found on Update/Delete

**Cause:** Resource doesn't exist

**Solution:**
- Verify the book ID is correct
- Check if book has been deleted by another user

### Issue: Missing Books in List

**Cause:** Filters applied incorrectly

**Solution:**
- Remove filters and check full list: `GET /api/books/`
- Verify query parameter names and values
- Check author ID exists: `GET /api/books/?author=1`

---

## Performance Considerations

1. **Queryset Optimization:**
   - Add `.select_related()` for foreign keys if needed
   - Use `.prefetch_related()` for reverse relationships

2. **Pagination:**
   - Default pagination helps manage large datasets
   - Configure in `settings.py` REST_FRAMEWORK settings

3. **Caching:**
   - Consider caching GET endpoints for read-only access
   - Use `cache_page` decorator for static content

---

## Security Notes

1. **Authentication:** IsAuthenticated ensures only logged-in users can modify data
2. **Permissions:** Use permission_classes to control access
3. **CSRF Protection:** Django's CSRF middleware protects POST/PUT/DELETE requests
4. **Input Validation:** Serializers validate all input data
5. **SQL Injection:** ORM prevents SQL injection through parameterized queries

---

## Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Generic Views Documentation](https://www.django-rest-framework.org/api-guide/generic-views/)
- [Permissions Documentation](https://www.django-rest-framework.org/api-guide/permissions/)
- [Serializers Documentation](https://www.django-rest-framework.org/api-guide/serializers/)
