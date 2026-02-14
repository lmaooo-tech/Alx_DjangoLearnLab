# Ordering Functionality - Testing & Examples Guide

## Quick Start

### Enable & Test Ordering

Ordering functionality is **already enabled** in BookListView. Simply use the `?ordering=` query parameter:

```bash
# Order by title ascending
curl http://localhost:8000/api/books/?ordering=title

# Order by publication year descending
curl http://localhost:8000/api/books/?ordering=-publication_year

# Combine with other parameters
curl "http://localhost:8000/api/books/?search=Tolkien&ordering=publication_year"
```

---

## Test Data Setup

Create sample books first to test ordering:

```bash
# Create Authors
POST /api/authors/create/
{"name": "J.R.R. Tolkien"}

POST /api/authors/create/
{"name": "Stephen King"}

POST /api/authors/create/
{"name": "George Orwell"}

# Create Books  
POST /api/books/create/
{"title": "The Hobbit", "publication_year": 1937, "author": 1}

POST /api/books/create/
{"title": "The Lord of the Rings", "publication_year": 1954, "author": 1}

POST /api/books/create/
{"title": "The Shining", "publication_year": 1977, "author": 2}

POST /api/books/create/
{"title": "The Stand", "publication_year": 1978, "author": 2}

POST /api/books/create/
{"title": "1984", "publication_year": 1949, "author": 3}
```

---

## Ordering Examples with cURL

### Example 1: Order by Title (A-Z)

```bash
curl "http://localhost:8000/api/books/?ordering=title"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 5, "title": "1984", "publication_year": 1949, "author": 3},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": 1},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": 1},
        {"id": 3, "title": "The Shining", "publication_year": 1977, "author": 2},
        {"id": 4, "title": "The Stand", "publication_year": 1978, "author": 2}
    ]
}
```

**Order:** Alphabetical (numbers first, then A-Z)

---

### Example 2: Order by Title (Z-A)

```bash
curl "http://localhost:8000/api/books/?ordering=-title"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 4, "title": "The Stand", "publication_year": 1978, "author": 2},
        {"id": 3, "title": "The Shining", "publication_year": 1977, "author": 2},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": 1},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": 1},
        {"id": 5, "title": "1984", "publication_year": 1949, "author": 3}
    ]
}
```

**Order:** Reverse alphabetical (Z-A)

---

### Example 3: Order by Publication Year (Date Ascending)

```bash
curl "http://localhost:8000/api/books/?ordering=publication_year"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": 1},
        {"id": 5, "title": "1984", "publication_year": 1949, "author": 3},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": 1},
        {"id": 3, "title": "The Shining", "publication_year": 1977, "author": 2},
        {"id": 4, "title": "The Stand", "publication_year": 1978, "author": 2}
    ]
}
```

**Order:** Oldest to newest (historical timeline)

---

### Example 4: Order by Publication Year (Date Descending - Default)

```bash
curl "http://localhost:8000/api/books/?ordering=-publication_year"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 4, "title": "The Stand", "publication_year": 1978, "author": 2},
        {"id": 3, "title": "The Shining", "publication_year": 1977, "author": 2},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": 1},
        {"id": 5, "title": "1984", "publication_year": 1949, "author": 3},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": 1}
    ]
}
```

**Note:** This is also the default ordering without ?ordering parameter!

---

### Example 5: Order by Author Name

```bash
curl "http://localhost:8000/api/books/?ordering=author__name"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 5, "title": "1984", "publication_year": 1949, "author": "George Orwell"},
        {"id": 3, "title": "The Shining", "publication_year": 1977, "author": "Stephen King"},
        {"id": 4, "title": "The Stand", "publication_year": 1978, "author": "Stephen King"},
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "J.R.R. Tolkien"},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": "J.R.R. Tolkien"}
    ]
}
```

**Order:** Alphabetical by author (George, Stephen, Tolkien)

---

### Example 6: Order by ID (Creation Order)

```bash
curl "http://localhost:8000/api/books/?ordering=id"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 1, "title": "The Hobbit", ...},
        {"id": 2, "title": "The Lord of the Rings", ...},
        {"id": 3, "title": "The Shining", ...},
        {"id": 4, "title": "The Stand", ...},
        {"id": 5, "title": "1984", ...}
    ]
}
```

**Order:** First added to last added

---

### Example 7: Order by ID (Reverse - Most Recent First)

```bash
curl "http://localhost:8000/api/books/?ordering=-id"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {"id": 5, "title": "1984", ...},
        {"id": 4, "title": "The Stand", ...},
        {"id": 3, "title": "The Shining", ...},
        {"id": 2, "title": "The Lord of the Rings", ...},
        {"id": 1, "title": "The Hobbit", ...}
    ]
}
```

**Order:** Last added to first added

---

### Example 8: Ordering with Filtering

Combine ordering with field filters:

```bash
curl "http://localhost:8000/api/books/?publication_year_min=1950&ordering=-publication_year"
```

**Result:** Books published after 1950, newest first

**Response:**
```json
{
    "count": 4,
    "results": [
        {"id": 4, "title": "The Stand", "publication_year": 1978},
        {"id": 3, "title": "The Shining", "publication_year": 1977},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954},
        {"id": 5, "title": "1984", "publication_year": 1949}  // Excluded
    ]
}
```

---

### Example 9: Ordering with Search

Combine ordering with text search:

```bash
curl "http://localhost:8000/api/books/?search=Tolkien&ordering=publication_year"
```

**Result:** Tolkien books, oldest first

**Response:**
```json
{
    "count": 2,
    "results": [
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, "author": "Tolkien"},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, "author": "Tolkien"}
    ]
}
```

---

### Example 10: Complex Query (Filter + Search + Ordering)

```bash
curl "http://localhost:8000/api/books/?search=The&publication_year_min=1950&ordering=title"
```

**Result:** Books with "The", published after 1950, sorted alphabetically

**Response:**
```json
{
    "count": 3,
    "results": [
        {"id": 3, "title": "The Shining", "publication_year": 1977},
        {"id": 4, "title": "The Stand", "publication_year": 1978},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954}
    ]
}
```

---

### Example 11: Order by Author with Filter

```bash
curl "http://localhost:8000/api/books/?author_name=King&ordering=-publication_year"
```

**Result:** Stephen King books, newest first

---

### Example 12: Order with Pagination

Ordering works across all pages:

```bash
# Page 1 (ordered by title)
curl "http://localhost:8000/api/books/?ordering=title&page=1"

# Page 2 (same ordering continues)
curl "http://localhost:8000/api/books/?ordering=title&page=2"
```

**Important:** Ordering is consistent across pagination

---

## Ordering Examples with Python

### Using Requests Library

```python
import requests

BASE_URL = 'http://localhost:8000/api/books/'

# Example 1: Order by title
response = requests.get(BASE_URL, params={'ordering': 'title'})
books = response.json()['results']
print([b['title'] for b in books])

# Example 2: Order newest first (default)
response = requests.get(BASE_URL, params={'ordering': '-publication_year'})
books = response.json()['results']

# Example 3: Order with filter
response = requests.get(BASE_URL, params={
    'publication_year_min': 1950,
    'ordering': '-publication_year'
})
books = response.json()['results']

# Example 4: Order with search
response = requests.get(BASE_URL, params={
    'search': 'King',
    'ordering': 'publication_year'
})
books = response.json()['results']

# Example 5: Complex query
response = requests.get(BASE_URL, params={
    'search': 'The',
    'publication_year_min': 1950,
    'author_name': 'King',
    'ordering': 'title'
})
books = response.json()['results']
print(f"Found {len(books)} books")
for book in books:
    print(f"  {book['title']} ({book['publication_year']})")
```

---

### Using DRF Test Client

```python
from rest_framework.test import APIClient

client = APIClient()

# Example 1: Order by title
response = client.get('/api/books/', {'ordering': 'title'})
assert response.status_code == 200
titles = [b['title'] for b in response.json()['results']]

# Example 2: Order with filtering
response = client.get('/api/books/', {
    'publication_year_min': 1950,
    'ordering': '-publication_year'
})
books = response.json()['results']

# Example 3: Invalid ordering field
response = client.get('/api/books/', {'ordering': 'invalid_field'})
assert response.status_code == 400
```

---

## Ordering Validation

### Test Case 1: Valid Ordering Fields

```python
def test_valid_ordering_fields():
    valid_fields = ['title', '-title', 'publication_year', '-publication_year',
                   'author__name', '-author__name', 'id', '-id']
    
    for field in valid_fields:
        response = client.get('/api/books/', {'ordering': field})
        assert response.status_code == 200
```

### Test Case 2: Invalid Ordering Field

```python
def test_invalid_ordering_field():
    response = client.get('/api/books/', {'ordering': 'invalid_field'})
    assert response.status_code == 400
    assert 'Invalid ordering field' in str(response.json())
```

### Test Case 3: Ordering is Consistent

```python
def test_ordering_consistency():
    response1 = client.get('/api/books/', {'ordering': 'title'})
    response2 = client.get('/api/books/', {'ordering': 'title'})
    
    ids1 = [b['id'] for b in response1.json()['results']]
    ids2 = [b['id'] for b in response2.json()['results']]
    
    assert ids1 == ids2  # Same order both times
```

### Test Case 4: Ascending vs. Descending

```python
def test_ascending_vs_descending():
    response_asc = client.get('/api/books/', {'ordering': 'publication_year'})
    response_desc = client.get('/api/books/', {'ordering': '-publication_year'})
    
    asc_ids = [b['id'] for b in response_asc.json()['results']]
    desc_ids = [b['id'] for b in response_desc.json()['results']]
    
    assert asc_ids == list(reversed(desc_ids))  # Opposite order
```

### Test Case 5: Ordering with Search

```python
def test_ordering_with_search():
    response = client.get('/api/books/', {
        'search': 'King',
        'ordering': 'publication_year'
    })
    assert response.status_code == 200
    books = response.json()['results']
    
    # Verify all results match search
    for book in books:
        assert 'King' in book['title'].lower() or 'King' in book['author'].lower()
    
    # Verify ordering
    years = [b['publication_year'] for b in books]
    assert years == sorted(years)  # Ascending order
```

---

## Ordering Performance Testing

### Test 1: Measure Ordering Speed

```python
import time

# Test ordering speed
start = time.time()
response = requests.get('http://localhost:8000/api/books/?ordering=-publication_year')
duration = time.time() - start

print(f"Ordering -publication_year: {duration*1000:.2f}ms")
```

### Test 2: Compare Order by Indexed vs. Unindexed

```python
# Fast (indexed field)
response1 = requests.get('.../api/books/?ordering=publication_year')

# Slower (unindexed field) - if any
response2 = requests.get('.../api/books/?ordering=other_field')
```

---

## Ordering with Pagination

### Pagination + Ordering Example

```bash
# First page, ordered by title
GET /api/books/?ordering=title&page=1

# Response has pagination information
{
    "count": 15,
    "next": "http://localhost:8000/api/books/?ordering=title&page=2",
    "previous": null,
    "results": [... 10 items ...]
}

# Get next page (same ordering)
GET /api/books/?ordering=title&page=2

# Response
{
    "count": 15,
    "next": "http://localhost:8000/api/books/?ordering=title&page=3",
    "previous": "http://localhost:8000/api/books/?ordering=title&page=1",
    "results": [... next 10 items ...]
}
```

---

## Troubleshooting Ordering

| Issue | Cause | Solution |
|-------|-------|----------|
| Results seem unordered | No ordering parameter, using default | Add ?ordering= parameter or check default |
| 400 Bad Request | Invalid field name | Use valid field: title, publication_year, author__name, id |
| Slow ordering queries | Field not indexed | Add db_index=True to model field |
| Results inconsistent across requests | No default ordering | Ensure ordering = [...] is set in view |
| Foreign key ordering returns error | Wrong syntax | Use double underscore: author__name not author.name |

---

## Common Ordering Patterns

### Pattern 1: Alphabetical Browsing

```python
# Get books alphabetically with pagination
response = requests.get(BASE_URL, params={
    'ordering': 'title',
    'page': 1
})
```

### Pattern 2: Latest Books

```python
# Default behavior - newest first
response = requests.get(BASE_URL)
# or explicit
response = requests.get(BASE_URL, params={'ordering': '-publication_year'})
```

### Pattern 3: Historical Timeline

```python
# Chronological order - oldest first
response = requests.get(BASE_URL, params={'ordering': 'publication_year'})
```

### Pattern 4: Author Directory

```python
# Browse by author alphabetically
response = requests.get(BASE_URL, params={'ordering': 'author__name'})
```

### Pattern 5: Search Results Sorted

```python
# Search and sort results
response = requests.get(BASE_URL, params={
    'search': query,
    'ordering': '-publication_year'
})
```

---

## Ordering API Reference

### Available Fields

```
title               - Book title (alphabetical)
-title              - Book title (reverse alphabetical)
publication_year    - Publication year (oldest first)
-publication_year   - Publication year (newest first) [DEFAULT]
author__name        - Author name (alphabetical)
-author__name       - Author name (reverse alphabetical)
id                  - Creation order (first added)
-id                 - Creation order (last added)
```

### Query Structure

```
GET /api/books/?ordering=FIELD

Where FIELD is one of:
- title  (ascending) or -title (descending)
- publication_year or -publication_year
- author__name or -author__name
- id or -id
```

---

## Summary

✅ **Ordering is enabled and ready to use**

**Key Features:**
- Sort by title, publication year, author, or ID
- Ascending (default) and descending order (prefix with `-`)
- Works with filters and search
- Database optimized
- Fully paginated

**Quick Reference:**
```bash
# Basic ordering
?ordering=title                      # A-Z
?ordering=-title                     # Z-A
?ordering=publication_year           # Oldest first
?ordering=-publication_year          # Newest first (DEFAULT)
?ordering=author__name               # Author A-Z

# With other parameters
?search=King&ordering=publication_year
?publication_year_min=1980&ordering=-publication_year
?author_name=King&ordering=title&page=1
```

---

**Status:** ✅ STEP 3 COMPLETE  
**Date:** February 14, 2026  
**Documentation Version:** 1.0
