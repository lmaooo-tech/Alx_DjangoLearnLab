# Book API - Filtering Setup Guide

## Quick Setup

### Step 1: Install django-filter

```bash
pip install django-filter==23.5
```

Or using the requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Verify settings.py Configuration

The following has been added to `settings.py`:

1. **INSTALLED_APPS** - Added `'django_filters'`
2. **REST_FRAMEWORK** - Configured default filter backends and pagination

### Step 3: Verify Imports in views.py

The following imports have been added:

```python
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, NumberFilter
```

### Step 4: Create Migrations (if needed)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Run the Application

```bash
python manage.py runserver
```

---

## Quick Start Examples

### List All Books (No Filters)
```bash
curl http://localhost:8000/api/books/
```

### Filter by Author Name
```bash
curl "http://localhost:8000/api/books/?author_name=Tolkien"
```

### Filter by Title
```bash
curl "http://localhost:8000/api/books/?title=Hobbit"
```

### Filter by Year Range
```bash
curl "http://localhost:8000/api/books/?publication_year_min=1930&publication_year_max=1960"
```

### Search Full-Text
```bash
curl "http://localhost:8000/api/books/?search=Ring"
```

### Sort by Title (A-Z)
```bash
curl "http://localhost:8000/api/books/?ordering=title"
```

### Sort by Publication Year (Newest First)
```bash
curl "http://localhost:8000/api/books/?ordering=-publication_year"
```

### Complex Query
```bash
curl "http://localhost:8000/api/books/?author_name=King&publication_year_min=1980&ordering=-publication_year"
```

---

## Features Implemented

### ✅ Field-Based Filtering (DjangoFilterBackend)

- Filter by `title` (substring, case-insensitive)
- Filter by `author_name` (substring, case-insensitive)
- Filter by `publication_year` (exact match)
- Filter by `publication_year_min` and `publication_year_max` (ranges)

### ✅ Full-Text Search (SearchFilter)

- Search across `title` and `author__name`
- `?search=value` parameter supported
- Case-insensitive searching

### ✅ Result Ordering (OrderingFilter)

- Sort by `title`, `publication_year`, `author__name`, `id`
- Support for ascending (`?ordering=field`) and descending (`?ordering=-field`)
- Default ordering: newest books first (`-publication_year`)

### ✅ Pagination

- Default page size: 10 items
- Configurable in `settings.py`

### ✅ Backward Compatibility

- Legacy query parameters still supported:
  - `?author=ID`
  - `?year_min=YEAR`
  - `?year_max=YEAR`

---

## Architecture

### BookFilterSet Class

Defines all available filters using django-filter's FilterSet:

- Provides declarative filter definitions
- Supports custom lookup expressions
- Linked to BookListView via `filterset_class`

### Filter Backends in BookListView

```python
filter_backends = [
    DjangoFilterBackend,      # Field-based filtering
    filters.SearchFilter,     # Full-text search
    filters.OrderingFilter    # Result sorting
]
```

### Query Execution Flow

1. User makes GET request with query parameters
2. DjangoFilterBackend processes `?field=value` parameters
3. SearchFilter processes `?search=term` parameter
4. OrderingFilter processes `?ordering=field` parameter
5. Combined queryset is paginated and returned

---

## Documentation Files

Detailed documentation is available in:

1. **ADVANCED_FILTERING_GUIDE.md**
   - Comprehensive filtering reference
   - Examples and use cases
   - Performance tips
   - Troubleshooting

2. **VIEWS_DOCUMENTATION.md**
   - View configuration details
   - API endpoint reference
   - Permission information
   - Logging configuration

---

## Testing Filters

### Using Python requests:

```python
import requests

# Filter by author name
response = requests.get('http://localhost:8000/api/books/', params={
    'author_name': 'Tolkien'
})
print(response.json())

# Search
response = requests.get('http://localhost:8000/api/books/', params={
    'search': 'Ring'
})
print(response.json())

# Complex filter + ordering
response = requests.get('http://localhost:8000/api/books/', params={
    'author_name': 'King',
    'publication_year_min': 1980,
    'ordering': '-publication_year'
})
print(response.json())
```

### Using curl:

```bash
# Multiple filters
curl 'http://localhost:8000/api/books/?author_name=Tolkien&publication_year_min=1930&ordering=publication_year'

# Search and filter
curl 'http://localhost:8000/api/books/?search=Lord&publication_year_max=1960'

# Just ordering
curl 'http://localhost:8000/api/books/?ordering=-title'
```

---

## Configuration Customization

### Add More Filters

Edit `BookFilterSet` in `views.py`:

```python
class BookFilterSet(FilterSet):
    # Add new filter
    isbn = CharFilter(
        field_name='isbn',
        lookup_expr='icontains'
    )
    
    class Meta:
        model = Book
        fields = []
```

### Change Default Page Size

Edit `settings.py`:

```python
REST_FRAMEWORK = {
    'PAGE_SIZE': 20,  # Change from 10 to 20
}
```

### Add More Search Fields

Edit `BookListView` in `views.py`:

```python
class BookListView(generics.ListAPIView):
    search_fields = [
        'title',
        'author__name',
        # 'isbn',  # Add if needed
    ]
```

### Add More Ordering Fields

Edit `BookListView`:

```python
class BookListView(generics.ListAPIView):
    ordering_fields = [
        'title',
        'publication_year',
        'author__name',
        'id',
        # 'isbn',  # Add if needed
    ]
```

---

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Start the server: `python manage.py runserver`
4. Test API endpoints with curl or Postman
5. Read `ADVANCED_FILTERING_GUIDE.md` for detailed usage

---

## Troubleshooting

### ImportError: No module named 'django_filters'

**Solution:** Install django-filter
```bash
pip install django-filter
```

### Filters not showing in API

**Solution:** Clear browser cache or add `'django_filters'` to `INSTALLED_APPS`

### 400 Bad Request on invalid ordering

**Solution:** Use only fields listed in `ordering_fields`

### No page parameter in response

**Solution:** Check pagination configuration in `settings.py` REST_FRAMEWORK settings

---

## Related Commands

```bash
# Run API tests
python manage.py test api

# Create superuser for Django admin
python manage.py createsuperuser

# Access Django admin
# Go to: http://localhost:8000/admin/

# Shell for testing
python manage.py shell
```

---

## API Response Example

```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        },
        {
            "id": 2,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        },
        {
            "id": 3,
            "title": "The Silmarillion",
            "publication_year": 1977,
            "author": 1
        }
    ]
}
```

---

## Performance Notes

- Filtering is applied at the database level (efficient)
- Use `select_related()` for foreign keys (already implemented)
- Pagination reduces load on large datasets
- Indexes on filtered fields improve performance

---

## Additional Resources

- [Django Filter Documentation](https://django-filter.readthedocs.io/)
- [DRF Filtering Guide](https://www.django-rest-framework.org/api-guide/filtering/)
- [Django Query Optimization](https://docs.djangoproject.com/en/6.0/topics/db/optimization/)
