# Search Functionality - Testing & Examples Guide

## Quick Start

### Enable & Test Search

Search functionality is **already enabled** in BookListView. Simply use the `?search=` query parameter:

```bash
# Basic search
curl http://localhost:8000/api/books/?search=Tolkien

# Search with other parameters
curl "http://localhost:8000/api/books/?search=King&publication_year_min=1980&ordering=-publication_year"
```

---

## Test Data Setup

Create sample books first to test search:

```bash
# Create Author: J.R.R. Tolkien
POST /api/authors/create/
{
    "name": "J.R.R. Tolkien"
}

# Create Book 1: The Hobbit
POST /api/books/create/
{
    "title": "The Hobbit",
    "publication_year": 1937,
    "author": 1
}

# Create Book 2: The Lord of the Rings
POST /api/books/create/
{
    "title": "The Lord of the Rings",
    "publication_year": 1954,
    "author": 1
}

# Create Author: Stephen King
POST /api/authors/create/
{
    "name": "Stephen King"
}

# Create Book 3: The Shining
POST /api/books/create/
{
    "title": "The Shining",
    "publication_year": 1977,
    "author": 3
}
```

---

## Search Examples with cURL

### Example 1: Search by Author Name

```bash
curl "http://localhost:8000/api/books/?search=Tolkien"
```

**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        },
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        },
        {
            "id": 3,
            "title": "The Shining (by different author)",
            "publication_year": 1977,
            "author": 3
        }
    ]
}
```

---

### Example 2: Search by Book Title

```bash
curl "http://localhost:8000/api/books/?search=Hobbit"
```

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        }
    ]
}
```

---

### Example 3: Partial String Search

Search for "The" (should find multiple books):

```bash
curl "http://localhost:8000/api/books/?search=The"
```

**Response:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        },
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        },
        {
            "id": 3,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 3
        }
    ]
}
```

---

### Example 4: Case-Insensitive Search

Search terms are case-insensitive:

```bash
# All these return the same results:
curl "http://localhost:8000/api/books/?search=tolkien"
curl "http://localhost:8000/api/books/?search=TOLKIEN"
curl "http://localhost:8000/api/books/?search=ToLkIeN"
```

---

### Example 5: Search + Year Filter

Find Stephen King books after 1970:

```bash
curl "http://localhost:8000/api/books/?search=King&publication_year_min=1970"
```

**Response:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 3,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 3
        }
    ]
}
```

---

### Example 6: Search + Ordering

Search for "The" and sort by title:

```bash
curl "http://localhost:8000/api/books/?search=The&ordering=title"
```

**Response:**
```json
{
    "count": 3,
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
            "title": "The Shining",
            "publication_year": 1977,
            "author": 3
        }
    ]
}
```

---

### Example 7: Search + Ordering (Descending)

Search for "Tolkien" sorted by newest year first:

```bash
curl "http://localhost:8000/api/books/?search=Tolkien&ordering=-publication_year"
```

**Response:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        },
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937,
            "author": 1
        }
    ]
}
```

---

### Example 8: Search + Multiple Filters + Ordering

Complex query:

```bash
curl "http://localhost:8000/api/books/?search=The&publication_year_min=1950&publication_year_max=1980&ordering=title"
```

**Result:** Books with "The" in title/author published between 1950-1980, sorted alphabetically

---

### Example 9: Empty Search

```bash
curl "http://localhost:8000/api/books/?search="
```

**Result:** Returns all books (empty search is ignored)

---

### Example 10: Non-existent Search

Search for something that doesn't exist:

```bash
curl "http://localhost:8000/api/books/?search=XYZ123NonExistent"
```

**Response:**
```json
{
    "count": 0,
    "results": []
}
```

---

## Search Examples with Python

### Using Requests Library

```python
import requests

# Base URL
BASE_URL = 'http://localhost:8000/api/books/'

# Example 1: Simple search
response = requests.get(BASE_URL, params={'search': 'Tolkien'})
books = response.json()['results']
print(f"Found {len(books)} books by Tolkien")

# Example 2: Search with filter
response = requests.get(BASE_URL, params={
    'search': 'King',
    'publication_year_min': 1980,
    'ordering': '-publication_year'
})
books = response.json()['results']
print(f"Found {len(books)} King books after 1980")

# Example 3: Iterating through paginated results
page = 1
all_results = []
while True:
    response = requests.get(BASE_URL, params={
        'search': 'The',
        'page': page
    })
    data = response.json()
    all_results.extend(data['results'])
    if not data['next']:
        break
    page += 1

print(f"Total results for 'The': {len(all_results)}")
```

---

### Using DRF Test Client

```python
from rest_framework.test import APIClient

client = APIClient()

# Example 1: Search
response = client.get('/api/books/', {'search': 'Tolkien'})
print(response.status_code)  # 200
books = response.json()['results']

# Example 2: Search with filter
response = client.get('/api/books/', {
    'search': 'Shining',
    'publication_year_min': 1970,
    'ordering': '-publication_year'
})
books = response.json()['results']
```

---

## Search Validation

### Test Case 1: Verify Search Works

```python
def test_search_finds_books():
    response = client.get('/api/books/?search=Hobbit')
    assert response.status_code == 200
    results = response.json()['results']
    assert len(results) > 0
    assert 'Hobbit' in results[0]['title']
```

### Test Case 2: Case Insensitivity

```python
def test_search_case_insensitive():
    response1 = client.get('/api/books/?search=tolkien')
    response2 = client.get('/api/books/?search=TOLKIEN')
    results1 = response1.json()['results']
    results2 = response2.json()['results']
    assert len(results1) == len(results2)
```

### Test Case 3: Partial Matching

```python
def test_search_partial_match():
    # Create books: "The Hobbit", "The Hobgoblin"
    response = client.get('/api/books/?search=hob')
    results = response.json()['results']
    assert len(results) == 2
```

### Test Case 4: Search with Filters

```python
def test_search_with_filter():
    response = client.get('/api/books/?search=King&publication_year_min=1980')
    results = response.json()['results']
    for book in results:
        assert 'King' in str(book['title']).lower() or 'King' in str(book['author']).lower()
        assert book['publication_year'] >= 1980
```

---

## Search Performance Tips

### 1. Use Indexed Fields

Add database indexes to frequently searched fields:

```python
class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        related_name='books'
    )

class Author(models.Model):
    name = models.CharField(max_length=200, db_index=True)
```

### 2. Use select_related()

Avoid N+1 queries when searching author names:

```python
def get_queryset(self):
    return Book.objects.select_related('author')
```

✅ This is already implemented in BookListView!

### 3. Limit Result Size

Use pagination to limit results per page:

```python
# Settings.py
REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
}
```

✅ This is already configured!

### 4. Add Caching for Popular Searches

```python
from django.views.decorators.cache import cache_page

class BookListView(generics.ListAPIView):
    @cache_page(60 * 5)  # Cache for 5 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Search returns no results | Check spelling, try lowercase, verify data exists |
| Search is slow | Add db_index=True to model fields, check select_related() |
| Special characters not found | URL encode them: space=%20, &=%26, etc. |
| Search seems case-sensitive | DRF SearchFilter is case-insensitive by default |
| Pagination with search doesn't work | Use ?search=term&page=2 format |

---

## Advanced Search Patterns

### Pattern 1: Autocomplete Search

```bash
# Get suggestions starting with "The"
curl "http://localhost:8000/api/books/?search=The&ordering=title&limit=5"
```

### Pattern 2: Multi-field Search Result

```python
# Search returns results where ANY field matches
# ?search=King could find:
# - "The Stand" by Stephen King (author match)
# - "King Lear" (title match)
# - "The King's Speech" (title match)
```

### Pattern 3: Combined Search + Filters + Ordering

```bash
curl "http://localhost:8000/api/books/?search=Lord&publication_year_min=1950&publication_year_max=1960&ordering=title"
```

---

## Search API Specification

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | No | None | Text to search in title and author name |
| title | string | No | None | Exact title filter |
| author_name | string | No | None | Exact author filter |
| publication_year_min | int | No | None | Minimum publication year |
| publication_year_max | int | No | None | Maximum publication year |
| ordering | string | No | -publication_year | Sort field (prefix with - for descending) |
| page | int | No | 1 | Page number for pagination |

### Response Format

```json
{
    "count": 10,
    "next": "http://localhost:8000/api/books/?search=term&page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "...",
            "publication_year": 1937,
            "author": 1
        }
    ]
}
```

---

## Summary

✅ **Search is enabled and ready to use**

**Key Features:**
- Case-insensitive text search
- Partial string matching
- Multi-field search (title + author)
- Combines with filters and ordering
- Database optimized
- Fully paginated

**Quick Reference:**
```bash
# Basic search
?search=Tolkien

# Search + filters
?search=King&publication_year_min=1980

# Search + ordering
?search=The&ordering=publication_year

# Complex query
?search=Game&author_name=Martin&publication_year=1996&ordering=-publication_year
```

---

**Status:** ✅ STEP 2 COMPLETE  
**Date:** February 14, 2026  
**Documentation Version:** 1.0
