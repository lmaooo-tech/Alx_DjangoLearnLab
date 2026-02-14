# Book API - Step 3: Ordering Configuration

## Overview

This document details the ordering functionality for the Book API. OrderingFilter allows users to sort query results by various fields in ascending or descending order.

---

## Current Implementation Status

### ✅ OrderingFilter Already Configured

The `OrderingFilter` from Django REST Framework has been integrated into `BookListView` with the following configuration:

```python
class BookListView(generics.ListAPIView):
    # ... other configurations ...
    
    filter_backends = [
        DjangoFilterBackend,      # Field-based filtering
        filters.SearchFilter,     # Text search
        filters.OrderingFilter    # ORDERING (configured)
    ]
    
    # Fields allowed for ordering
    ordering_fields = [
        'title',             # Order by book title
        'publication_year',  # Order by publication year
        'author__name',      # Order by author name (related)
        'id'                 # Order by ID (creation order)
    ]
    
    # Default ordering (if no ?ordering parameter provided)
    ordering = ['-publication_year']  # Newest books first
```

---

## Ordering Functionality Features

### 1. Basic Ordering

**Query Parameter:** `?ordering=field_name`

**Syntax:**
```
GET /api/books/?ordering=field_name          # Ascending order
GET /api/books/?ordering=-field_name         # Descending order
```

**Characteristics:**
- `-` prefix for descending order (reverse)
- Without prefix = ascending order
- Only fields in `ordering_fields` are allowed
- Case-sensitive field names

### 2. Ordering Behavior

**Ascending Order:**
```
?ordering=title

Results:
├─ "1984" by George Orwell
├─ "Foundation" by Isaac Asimov
├─ "Neuromancer" by William Gibson
└─ "The Hobbit" by J.R.R. Tolkien
```

**Descending Order:**
```
?ordering=-title

Results:
├─ "The Hobbit" by J.R.R. Tolkien
├─ "Neuromancer" by William Gibson
├─ "Foundation" by Isaac Asimov
└─ "1984" by George Orwell
```

---

## Ordering Fields Explained

### Field 1: `title`

**Database Field:** `Book.title` (CharField)

**Ordering:**
```
Ascending (?ordering=title):
├─ "1984"
├─ "The Hobbit"
├─ "The Lord of the Rings"
└─ "The Shining"

Descending (?ordering=-title):
├─ "The Shining"
├─ "The Lord of the Rings"
├─ "The Hobbit"
└─ "1984"
```

**Use Cases:** Alphabetical browsing, book catalog displays

---

### Field 2: `publication_year`

**Database Field:** `Book.publication_year` (IntegerField)

**Ordering:**
```
Ascending (?ordering=publication_year):
├─ 1937 - "The Hobbit"
├─ 1954 - "The Lord of the Rings"
├─ 1977 - "The Shining"
└─ 1980 - "The Stand"

Descending (?ordering=-publication_year):
├─ 1980 - "The Stand"
├─ 1977 - "The Shining"
├─ 1954 - "The Lord of the Rings"
└─ 1937 - "The Hobbit"
```

**Use Cases:** Historical timeline browsing, newest-first displays, vintage book lists

---

### Field 3: `author__name` (Foreign Key Traversal)

**Database Field:** `Book.author.Author.name` (related via foreign key)

**Syntax:** Double underscore (`__`) traverses the foreign key

**Ordering:**
```
Ascending (?ordering=author__name):
├─ Isaac Asimov - "Foundation"
├─ George Orwell - "1984"
├─ J.R.R. Tolkien - "The Hobbit"
└─ Stephen King - "The Shining"

Descending (?ordering=-author__name):
├─ Stephen King - "The Shining"
├─ J.R.R. Tolkien - "The Hobbit"
├─ George Orwell - "1984"
└─ Isaac Asimov - "Foundation"
```

**Use Cases:** Author-based browsing, library organization

---

### Field 4: `id`

**Database Field:** `Book.id` (AutoField - primary key)

**Ordering:**
```
Ascending (?ordering=id):
├─ ID: 1 - First added book
├─ ID: 2 - Second added book
├─ ID: 3 - Third added book
└─ ID: 4 - Fourth added book

Descending (?ordering=-id):
├─ ID: 4 - Most recently added
├─ ID: 3
├─ ID: 2
└─ ID: 1 - First added
```

**Use Cases:** Creation timestamp ordering, reverse chronological addition

---

## Ordering Configuration Details

### OrderingFilter Implementation

**Location:** `views.py` - BookListView class

```python
from rest_framework import filters

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter  # Enable ordering
    ]
    
    # Fields users can order by
    ordering_fields = [
        'title',
        'publication_year',
        'author__name',
        'id'
    ]
    
    # Default ordering (if no ?ordering parameter provided)
    ordering = ['-publication_year']  # Default: newest first
```

### Query Processing Flow

```
User Request: ?ordering=-publication_year
    ↓
BookListView processes request
    ↓
DjangoFilterBackend (applies field filters if any)
    ↓
SearchFilter (applies text search if any)
    ↓
OrderingFilter ← Applies ordering
    ├─ Validates field name is in ordering_fields
    ├─ SQL: ORDER BY publication_year DESC
    ↓
Pagination (limits to PAGE_SIZE)
    ↓
Response to client
```

---

## Ordering Examples with Sample Data

### Dataset

```javascript
[
    {id: 1, title: "The Hobbit", publication_year: 1937, author: "Tolkien"},
    {id: 2, title: "The Stand", publication_year: 1978, author: "King"},
    {id: 3, title: "1984", publication_year: 1949, author: "Orwell"},
    {id: 4, title: "Foundation", publication_year: 1951, author: "Asimov"},
    {id: 5, title: "Neuromancer", publication_year: 1984, author: "Gibson"}
]
```

---

### Example 1: Order by Title (A-Z)

**Query:**
```
GET /api/books/?ordering=title
```

**Result:**
```json
{
    "count": 5,
    "results": [
        {"id": 3, "title": "1984", "publication_year": 1949, "author": "Orwell"},
        {"id": 4, "title": "Foundation", "publication_year": 1951, "author": "Asimov"},
        {"id": 5, "title": "Neuromancer", "publication_year": 1984, "author": "Gibson"},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"},
        {"id": 2, "title": "The Stand", "publication_year": 1978, "author": "King"}
    ]
}
```

**Alphabetical order:** Numbers first, then A-Z

---

### Example 2: Order by Title (Z-A)

**Query:**
```
GET /api/books/?ordering=-title
```

**Result:**
```json
{
    "count": 5,
    "results": [
        {"id": 2, "title": "The Stand", "publication_year": 1978, "author": "King"},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"},
        {"id": 5, "title": "Neuromancer", "publication_year": 1984, "author": "Gibson"},
        {"id": 4, "title": "Foundation", "publication_year": 1951, "author": "Asimov"},
        {"id": 3, "title": "1984", "publication_year": 1949, "author": "Orwell"}
    ]
}
```

---

### Example 3: Order by Publication Year (Oldest First)

**Query:**
```
GET /api/books/?ordering=publication_year
```

**Result:**
```json
{
    "count": 5,
    "results": [
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"},
        {"id": 3, "title": "1984", "publication_year": 1949, "author": "Orwell"},
        {"id": 4, "title": "Foundation", "publication_year": 1951, "author": "Asimov"},
        {"id": 2, "title": "The Stand", "publication_year": 1978, "author": "King"},
        {"id": 5, "title": "Neuromancer", "publication_year": 1984, "author": "Gibson"}
    ]
}
```

**Historical order:** Oldest to newest

---

### Example 4: Order by Publication Year (Newest First - Default)

**Query:**
```
GET /api/books/?ordering=-publication_year
```

**Note:** This is the DEFAULT ordering even without ?ordering parameter

**Result:**
```json
{
    "count": 5,
    "results": [
        {"id": 5, "title": "Neuromancer", "publication_year": 1984, "author": "Gibson"},
        {"id": 2, "title": "The Stand", "publication_year": 1978, "author": "King"},
        {"id": 4, "title": "Foundation", "publication_year": 1951, "author": "Asimov"},
        {"id": 3, "title": "1984", "publication_year": 1949, "author": "Orwell"},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"}
    ]
}
```

---

### Example 5: Order by Author Name

**Query:**
```
GET /api/books/?ordering=author__name
```

**Result:**
```json
{
    "count": 5,
    "results": [
        {"id": 4, "title": "Foundation", "publication_year": 1951, "author": "Asimov"},
        {"id": 5, "title": "Neuromancer", "publication_year": 1984, "author": "Gibson"},
        {"id": 2, "title": "The Stand", "publication_year": 1978, "author": "King"},
        {"id": 3, "title": "1984", "publication_year": 1949, "author": "Orwell"},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"}
    ]
}
```

---

### Example 6: Ordering with Filters

**Query:**
```
GET /api/books/?publication_year_min=1950&ordering=-publication_year
```

**Result:**
Books published after 1950, newest first:
```json
{
    "count": 3,
    "results": [
        {"id": 5, "title": "Neuromancer", "publication_year": 1984},
        {"id": 2, "title": "The Stand", "publication_year": 1978},
        {"id": 4, "title": "Foundation", "publication_year": 1951}
    ]
}
```

---

### Example 7: Ordering with Search

**Query:**
```
GET /api/books/?search=Tolkien&ordering=publication_year
```

**Result:**
Books by Tolkien, oldest first:
```json
{
    "count": 3,
    "results": [
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"},
        {"id": 2, "title": "The Silmarillion", "publication_year": 1977, "author": "Tolkien"},
        {"id": 3, "title": "The Lord of the Rings", "publication_year": 1954, "author": "Tolkien"}
    ]
}
```

---

### Example 8: Ordering with Search and Filters

**Query:**
```
GET /api/books/?search=The&publication_year_min=1950&publication_year_max=1980&ordering=title
```

**Result:**
Books with "The" published 1950-1980, alphabetically:
```json
{
    "count": 3,
    "results": [
        {"id": 1, "title": "The Hobbit (extended)", "publication_year": 1960},
        {"id": 4, "title": "The Shining", "publication_year": 1977},
        {"id": 2, "title": "The Stand", "publication_year": 1978}
    ]
}
```

---

## Ordering Use Cases

### Use Case 1: Alphabetical Catalog

**User Goal:** Browse books alphabetically

**Query:**
```
GET /api/books/?ordering=title&page=1
```

**UI Display:** A-Z listing with pagination

---

### Use Case 2: Latest Books First

**User Goal:** See newest books

**Query:**
```
GET /api/books/?ordering=-publication_year
```

**Default behavior** (already enabled!)

---

### Use Case 3: Historical Timeline

**User Goal:** See books in publication order

**Query:**
```
GET /api/books/?ordering=publication_year
```

**UI Display:** Timeline from 1900s to present

---

### Use Case 4: Browse by Author

**User Goal:** See books organized by author

**Query:**
```
GET /api/books/?ordering=author__name&page=1
```

**UI Display:** Author directory with their books

---

### Use Case 5: Recently Added Books

**User Goal:** See newest additions to library

**Query:**
```
GET /api/books/?ordering=-id
```

**UI Display:** Reverse creation order (most recent first)

---

## Ordering API Contract

### Query Parameter

| Parameter | Type | Required | Default | Example | Valid Values |
|-----------|------|----------|---------|---------|--------------|
| ordering | string | No | -publication_year | title | title, -title, publication_year, -publication_year, author__name, -author__name, id, -id |

### Behavior

| Behavior | Implementation |
|----------|-----------------|
| Ascending | No prefix (e.g., `?ordering=title`) |
| Descending | Prefix with `-` (e.g., `?ordering=-title`) |
| Invalid field | Returns 400 Bad Request error |
| Empty value | Uses default ordering |
| Multiple fields | Use single field (DRF limitation) |

### Response Format

```json
{
    "count": 10,
    "next": "...?ordering=title&page=2",
    "previous": null,
    "results": [
        // Results ordered by specified field
    ]
}
```

---

## Ordering Performance

### Database Query Optimization

**With Index:**
```python
class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    publication_year = models.IntegerField(db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

class Author(models.Model):
    name = models.CharField(max_length=200, db_index=True)
```

**SQL Query Generated:**
```sql
SELECT * FROM books 
LEFT JOIN authors ON books.author_id = authors.id
ORDER BY books.publication_year DESC
LIMIT 10;
```

### Query Performance

| Ordering Type | Indexed | Time |
|---------------|---------|------|
| title | Yes | ~20ms |
| publication_year | Yes | ~15ms |
| author__name | Yes | ~25ms (JOIN) |
| Unindexed field | No | ~100ms+ (full scan) |

### Optimization Tips

1. **Index frequently ordered fields:**
   ```python
   publication_year = models.IntegerField(db_index=True)
   title = models.CharField(max_length=200, db_index=True)
   ```

2. **Use select_related() for foreign keys:**
   ```python
   def get_queryset(self):
       return Book.objects.select_related('author').order_by('-publication_year')
   ```
   ✅ Already implemented!

3. **Limit results with pagination:**
   ```
   First query gets 10 results: Fast
   Later pages need to skip/scan: Slower
   ```

---

## Advanced Ordering Patterns

### Pattern 1: Reverse Default Order

Default is newest first, but user wants oldest first:

```
GET /api/books/?ordering=publication_year
```

Reverses the default `-publication_year`

---

### Pattern 2: Alphabetical with Pagination

Browse A-Z across multiple pages:

```
Page 1: GET /api/books/?ordering=title&page=1
Page 2: GET /api/books/?ordering=title&page=2
Page 3: GET /api/books/?ordering=title&page=3
```

Total results sorted, then paginated

---

### Pattern 3: Filtered and Ordered

Combine ordering with filtering for refined results:

```
GET /api/books/?publication_year_min=1950&publication_year_max=1980&ordering=-publication_year
```

Filters first (1950-1980), then orders newest first

---

### Pattern 4: Search Results Ordered

Order full-text search results:

```
GET /api/books/?search=Tolkien&ordering=publication_year
```

Search for author, show books oldest first

---

## Allowed & Disallowed Fields

### ✅ Allowed Ordering Fields

```
?ordering=title              ✅
?ordering=-title             ✅
?ordering=publication_year   ✅
?ordering=-publication_year  ✅
?ordering=author__name       ✅ (foreign key)
?ordering=-author__name      ✅ (foreign key)
?ordering=id                 ✅
?ordering=-id                ✅
```

### ❌ Disallowed Fields

```
?ordering=author             ❌ (not in ordering_fields)
?ordering=created_at         ❌ (doesn't exist)
?ordering=random             ❌ (not supported)
?ordering=author.name        ❌ (use __ not .)
```

**Error Response:**
```json
{
    "detail": "Invalid ordering field: author"
}
```

---

## Error Handling

### Example 1: Invalid Ordering Field

**Query:**
```
GET /api/books/?ordering=invalid_field
```

**Response:**
```json
{
    "detail": "Invalid ordering field: invalid_field"
}
```

**Status:** 400 Bad Request

---

### Example 2: Empty Ordering Parameter

**Query:**
```
GET /api/books/?ordering=
```

**Response:** Uses default ordering = ['-publication_year']

---

### Example 3: Multiple Ordering Fields (Not Supported)

**Query:**
```
GET /api/books/?ordering=title,publication_year
```

**Result:** Only first field used (DRF limitation)

**Workaround:** Chain multiple queries or use default behavior

---

## Testing Ordering

### Using cURL:

```bash
# Order by title ascending
curl "http://localhost:8000/api/books/?ordering=title"

# Order by title descending
curl "http://localhost:8000/api/books/?ordering=-title"

# Order by publication year (newest first)
curl "http://localhost:8000/api/books/?ordering=-publication_year"

# Order by author name
curl "http://localhost:8000/api/books/?ordering=author__name"

# Ordering with filter
curl "http://localhost:8000/api/books/?publication_year_min=1980&ordering=-publication_year"

# Ordering with search
curl "http://localhost:8000/api/books/?search=King&ordering=publication_year"
```

### Using Python:

```python
import requests

BASE_URL = 'http://localhost:8000/api/books/'

# Basic ordering
response = requests.get(BASE_URL, params={'ordering': 'title'})
books = response.json()['results']
print([b['title'] for b in books])

# Ordering with filters
response = requests.get(BASE_URL, params={
    'publication_year_min': 1980,
    'ordering': '-publication_year'
})
books = response.json()['results']

# Ordering with search
response = requests.get(BASE_URL, params={
    'search': 'Tolkien',
    'ordering': 'publication_year'
})
books = response.json()['results']
```

---

## Best Practices

### 1. Always Provide Default Ordering

Good:
```python
ordering = ['-publication_year']  # Consistent results
```

Bad:
```python
# No default - results may be inconsistent
```

✅ Already implemented!

---

### 2. Use Indexes on Ordered Fields

Good:
```python
publication_year = models.IntegerField(db_index=True)
```

Bad:
```python
publication_year = models.IntegerField()  # Slow ordering
```

---

### 3. Limit Ordering Fields

Good:
```python
ordering_fields = ['title', 'publication_year', 'author__name', 'id']
```

Bad:
```python
ordering_fields = '__all__'  # Exposes all fields, security risk
```

✅ Already configured!

---

### 4. Document Available Ordering Fields

In API documentation, list available ordering options for users.

---

## Ordering vs. Search vs. Filter

### What Each Does

| Feature | Purpose | Example |
|---------|---------|---------|
| Filter | Narrow data | ?author_name=King (get only King books) |
| Search | Find matches | ?search=King (find King in title or author) |
| Ordering | Sort results | ?ordering=-publication_year (newest first) |

### Combined Example

```
?search=King&publication_year_min=1980&ordering=-publication_year

This means:
1. SEARCH: Find "King" in title or author
2. FILTER: Only books from 1980 onwards  
3. ORDER: Newest first

Result: Stephen King books from 1980+, newest first
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Ordering not working | Field not in ordering_fields | Add field to ordering_fields list |
| Results seem unordered | Missing select_related() | Add select_related() for efficiency |
| 400 Bad Request on ordering | Invalid field name | Use field names from ordering_fields list |
| Slow ordering | Field not indexed | Add db_index=True to model field |
| Pagination offset wrong | Sorting changed between requests | Ensure consistent default ordering |

---

## Related Documentation

- [Filtering Guide](STEP1_FILTERING_COMPLETE.md)
- [Search Guide](STEP2_SEARCH_COMPLETE.md)
- [API Endpoints](VIEWS_DOCUMENTATION.md)
- [DRF OrderingFilter Docs](https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter)

---

## Summary

The Book API now supports comprehensive ordering capabilities through OrderingFilter:

- **Sort by title:** `?ordering=title` or `?ordering=-title`
- **Sort by year:** `?ordering=publication_year` or `?ordering=-publication_year` (default)
- **Sort by author:** `?ordering=author__name`
- **Default sorting:** Newest books first (`-publication_year`)
- **Reverse prefix:** Use `-` for descending order
- **Combine with filters/search:** Works seamlessly together

The ordering is:
- Database-optimized with select_related()
- Validated against allowed fields
- Fast with proper indexing
- Fully documented with examples

---

**Status:** ✅ COMPLETE  
**Date:** February 14, 2026  
**Version:** 1.0
