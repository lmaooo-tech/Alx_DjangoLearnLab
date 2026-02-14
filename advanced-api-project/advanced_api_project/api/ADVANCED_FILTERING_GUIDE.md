# Book API - Advanced Filtering Guide

## Overview

The Book API now provides comprehensive filtering, searching, and ordering capabilities through Django REST Framework's powerful filtering backends. This document explains how to use these advanced features.

---

## Installation Requirements

Ensure that `django-filter` is installed in your project:

```bash
pip install django-filter
```

Add `django_filters` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'django_filters',  # Add this line
    'api',
]
```

Configure default filter backend in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

---

## Filtering Types

### 1. Field-Based Filtering (DjangoFilterBackend)

Filters books by specific field values and ranges.

#### Available Filters:

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `title` | String (partial) | Case-insensitive substring search in book title | `?title=Hobbit` |
| `author_name` | String (partial) | Case-insensitive substring search in author name | `?author_name=Tolkien` |
| `publication_year` | Integer | Exact year match | `?publication_year=1937` |
| `publication_year_min` | Integer | Minimum year (inclusive) | `?publication_year_min=1930` |
| `publication_year_max` | Integer | Maximum year (inclusive) | `?publication_year_max=1950` |

#### Filter Examples:

**Filter by Title (substring, case-insensitive):**
```
GET /api/books/?title=Hobbit
GET /api/books/?title=rings
GET /api/books/?title=game (returns "A Game of Thrones", "The Game...")
```

**Filter by Author Name (substring, case-insensitive):**
```
GET /api/books/?author_name=Tolkien
GET /api/books/?author_name=king (returns books by "Stephen King", "King Author", etc.)
```

**Filter by Exact Publication Year:**
```
GET /api/books/?publication_year=1937
GET /api/books/?publication_year=2001
```

**Filter by Year Range:**
```
GET /api/books/?publication_year_min=1930
GET /api/books/?publication_year_max=1950
GET /api/books/?publication_year_min=1930&publication_year_max=1950
```

**Combine Multiple Filters:**
```
GET /api/books/?title=Lord&publication_year_min=1950
GET /api/books/?author_name=Tolkien&publication_year=1954
GET /api/books/?author_name=King&publication_year_min=1980&publication_year_max=2000
GET /api/books/?title=Game&author_name=Martin
```

---

### 2. Full-Text Search (SearchFilter)

Search across multiple fields simultaneously with the `?search` parameter.

#### Search Configuration:

Fields included in search:
- `title` - Book title
- `author__name` - Author name (via foreign key)

#### Search Examples:

**Basic Search:**
```
GET /api/books/?search=Ring
(Returns books matching "Ring" in title or author name)

GET /api/books/?search=Tolkien
(Returns books by authors with "Tolkien" in name or with "Tolkien" in title)

GET /api/books/?search=1954
(Searches for "1954" in searchable fields - may not return results unless in title)
```

**Search is Case-Insensitive:**
```
GET /api/books/?search=hobbit
GET /api/books/?search=HOBBIT
GET /api/books/?search=Hobbit
(All three return the same results)
```

**Search Matches Partial Strings:**
```
GET /api/books/?search=Tol
(Returns books by Tolkien, books with "Tol" in title, etc.)
```

**Advanced: Combine Search with Filters:**
```
GET /api/books/?search=Ring&publication_year_min=1950
(Search for "Ring" AND filter by year >= 1950)

GET /api/books/?search=Lord&author_name=Tolkien
(Search for "Lord" AND author contains "Tolkien")
```

---

### 3. Ordering (OrderingFilter)

Sort results by different fields.

#### Available Ordering Fields:

| Field | Description | Example Ascending | Example Descending |
|-------|-------------|-------------------|-------------------|
| `title` | Book title alphabetically | `?ordering=title` | `?ordering=-title` |
| `publication_year` | Publication year | `?ordering=publication_year` | `?ordering=-publication_year` |
| `author__name` | Author name alphabetically | `?ordering=author__name` | `?ordering=-author__name` |
| `id` | ID (creation order) | `?ordering=id` | `?ordering=-id` |

#### Ordering Examples:

**Sort by Title (A-Z):**
```
GET /api/books/?ordering=title
Results: A Game of Thrones, The Hobbit, The Shining, ...
```

**Sort by Title (Z-A - reverse):**
```
GET /api/books/?ordering=-title
Results: The Shining, The Hobbit, A Game of Thrones, ...
```

**Sort by Publication Year (Oldest First):**
```
GET /api/books/?ordering=publication_year
Results: 1930s books, 1940s books, ... recent books
```

**Sort by Publication Year (Newest First - Default):**
```
GET /api/books/?ordering=-publication_year
```

**Sort by Author Name (A-Z):**
```
GET /api/books/?ordering=author__name
Results: Books by authors A-Z (Asimov, Christie, King, etc.)
```

**Sort by Author Name (Z-A):**
```
GET /api/books/?ordering=-author__name
```

**Combine Ordering with Filters:**
```
GET /api/books/?author_name=Tolkien&ordering=publication_year
(Show Tolkien's books ordered by publication year, earliest first)

GET /api/books/?publication_year_min=1980&ordering=title
(Show books after 1980, sorted by title)
```

---

## Combined Query Examples

### Example 1: Complex Filter + Ordering
```
GET /api/books/?author_name=Tolkien&publication_year_min=1930&ordering=publication_year

Returns:
- All books by Tolkien (name contains "Tolkien")
- Published in 1930 or later
- Ordered by publication year (oldest first)
```

**Response (example):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        },
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
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

### Example 2: Search + Multiple Filters + Ordering
```
GET /api/books/?search=Ring&publication_year_min=1950&publication_year_max=1960&ordering=title

Returns:
- Books matching "Ring" in title or author name
- Published between 1950 and 1960
- Sorted by title alphabetically
```

### Example 3: Year Range Filtering + Reverse Ordering
```
GET /api/books/?publication_year_min=1980&publication_year_max=2000&ordering=-title

Returns:
- Books published between 1980 and 2000 (inclusive)
- Sorted by title in reverse alphabetical order (Z-A)
```

### Example 4: Author Search + Newest First
```
GET /api/books/?author_name=King&ordering=-publication_year

Returns:
- All books by authors with "King" in their name
- Newest books first
```

---

## Implementation Details

### BookFilterSet Class

The `BookFilterSet` class defines all available filters:

```python
class BookFilterSet(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',  # Case-insensitive contains
        label='Search by title (partial match)',
    )
    
    author_name = CharFilter(
        field_name='author__name',  # Foreign key traversal
        lookup_expr='icontains',
        label='Search by author name (partial match)',
    )
    
    publication_year = NumberFilter(
        field_name='publication_year',
        label='Exact year filter',
    )
    
    publication_year_min = NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',  # >= (greater than or equal)
        label='Minimum publication year',
    )
    
    publication_year_max = NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',  # <= (less than or equal)
        label='Maximum publication year',
    )
```

### BookListView Configuration

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all().order_by('-publication_year')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # Filtering backends
    filter_backends = [
        DjangoFilterBackend,      # Field-based filtering
        filters.SearchFilter,     # Text search
        filters.OrderingFilter    # Sorting
    ]
    
    # Filter configuration
    filterset_class = BookFilterSet
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name', 'id']
    ordering = ['-publication_year']  # Default ordering
```

---

## Query Parameter Reference

### Syntax

```
GET /api/books/?filter1=value1&filter2=value2&search=searchterm&ordering=field
```

### Parameter Types

| Parameter Type | Syntax | Example |
|---|---|---|
| Filter (equality) | `?field=value` | `?publication_year=1937` |
| Filter (range min) | `?field_min=value` | `?publication_year_min=1930` |
| Filter (range max) | `?field_max=value` | `?publication_year_max=1950` |
| Search | `?search=term` | `?search=Ring` |
| Ordering (asc) | `?ordering=field` | `?ordering=title` |
| Ordering (desc) | `?ordering=-field` | `?ordering=-publication_year` |

### Multiple Values

To use multiple filters and searches:
```
?filter1=value1&filter2=value2&search=term&ordering=field
```

---

## Backward Compatibility

The API maintains backward compatibility with legacy query parameters:

**Legacy Parameters (still supported):**
```
?author=ID           # Filter by author ID
?year_min=YEAR       # Minimum publication year
?year_max=YEAR       # Maximum publication year
```

**Recommended (new parameters):**
```
?author_name=NAME    # Filter by author name (substring)
?publication_year_min=YEAR  # Minimum publication year
?publication_year_max=YEAR  # Maximum publication year
```

---

## Performance Considerations

### Optimization Tips

1. **Use `select_related()` for Foreign Keys:** Already implemented in `get_queryset()`
   ```python
   queryset = Book.objects.all().select_related('author')
   ```

2. **Pagination:** Default pagination reduces load on large datasets
   - Configure in settings: `PAGE_SIZE = 10`

3. **Database Indexing:** Ensure fields used in filters are indexed
   ```python
   class Book(models.Model):
       title = models.CharField(max_length=200, db_index=True)
       publication_year = models.IntegerField(db_index=True)
```

4. **Avoid Excessive Filtering:** Complex filters with many OR conditions can be slow

### Example: Efficient Query
```
GET /api/books/?author_name=Tolkien&publication_year_min=1930&ordering=publication_year
```
This is efficient because:
- Uses indexed fields
- Exact and range filters (not regex)
- Single related object lookup (select_related)

---

## Error Handling

### Invalid Filter Values

**Invalid year (non-numeric):**
```
GET /api/books/?publication_year=invalid

Response: Filter is ignored, returns all books
(Graceful error handling - invalid values don't break the API)
```

**Invalid ordering field:**
```
GET /api/books/?ordering=invalid_field

Response (400 Bad Request):
{
    "detail": "Invalid ordering field: invalid_field"
}
```

---

## Testing Filtering

### Python requests library:
```python
import requests

# Filter by author name
response = requests.get('http://localhost:8000/api/books/', params={
    'author_name': 'Tolkien',
    'publication_year_min': 1930
})

# Search
response = requests.get('http://localhost:8000/api/books/', params={
    'search': 'Ring'
})

# Order
response = requests.get('http://localhost:8000/api/books/', params={
    'ordering': 'title'
})
```

### cURL:
```bash
# Filter by title
curl "http://localhost:8000/api/books/?title=Hobbit"

# Filter and search combined
curl "http://localhost:8000/api/books/?author_name=Tolkien&search=Ring"

# With ordering
curl "http://localhost:8000/api/books/?publication_year_min=1950&ordering=-publication_year"
```

---

## Advanced Usage

### Custom Filter Backends

To add custom filtering logic, override `get_queryset()`:

```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Custom logic
    if self.request.user.is_staff:
        # Staff users see all books
        return queryset
    else:
        # Regular users see only published books
        return queryset.filter(published=True)
```

### Adding New Filters

To add a new filter to the API:

1. Add to `BookFilterSet`:
```python
class BookFilterSet(FilterSet):
    isbn = CharFilter(
        field_name='isbn',
        lookup_expr='icontains'
    )
```

2. Add to Book model if needed:
```python
class Book(models.Model):
    isbn = models.CharField(max_length=20)
```

---

## API Response Structure

All list responses include:

```json
{
    "count": 10,
    "next": "http://localhost:8000/api/books/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Book Title",
            "publication_year": 1937,
            "author": 1
        },
        ...
    ]
}
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Filters not working | `django-filter` not installed or not in INSTALLED_APPS | Install package and add to settings |
| 400 Bad Request on invalid ordering | Invalid field name | Use only allowed ordering fields |
| No results when filtering | Filter values don't match data | Check data in database, use browser DevTools |
| Slow queries | Too many filters or unindexed fields | Add indexes, optimize queries |

---

## See Also

- [Django REST Framework Filtering Documentation](https://www.django-rest-framework.org/api-guide/filtering/)
- [django-filter Documentation](https://django-filter.readthedocs.io/)
- [DjangoFilterBackend Documentation](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend)
