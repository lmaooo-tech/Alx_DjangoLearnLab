# STEP 4: API Views Integration - Practical Usage Guide

## Complete API Overview

The Book API now has fully integrated filtering, searching, and ordering across all views.

---

## Available Endpoints (After Step 4)

### Book Endpoints

| Endpoint | Method | Features | Auth Required |
|----------|--------|----------|---------------|
| `/api/books/` | GET | List, Filter, Search, Order, Paginate | No |
| `/api/books/create/` | POST | Create book | Yes |
| `/api/books/<id>/` | GET | Get single book | No |
| `/api/books/<id>/update/` | PUT/PATCH | Update book | Yes |
| `/api/books/<id>/delete/` | DELETE | Delete book | Yes |

### Author Endpoints

| Endpoint | Method | Features | Auth Required |
|----------|--------|----------|---------------|
| `/api/authors/` | GET | List, Search, Order, Paginate | No |
| `/api/authors/create/` | POST | Create author | Yes |
| `/api/authors/<id>/` | GET | Get author + books | No |
| `/api/authors/<id>/update/` | PUT/PATCH | Update author | Yes |
| `/api/authors/<id>/delete/` | DELETE | Delete author | Yes |

---

## Book API - Complete Query Examples

### Example 1: List All Books (Default)

```bash
curl http://localhost:8000/api/books/
```

**Response:**
```json
{
    "count": 152,
    "next": "http://localhost:8000/api/books/?page=2",
    "previous": null,
    "results": [
        {
            "id": 12,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 5
        },
        ...
    ]
}
```

**Ordering:** Newest books first (default: `-publication_year`)

---

### Example 2: Filter Books by Author

```bash
curl "http://localhost:8000/api/books/?author_name=Tolkien"
```

**Result:** All books by any author with "Tolkien" in name

---

### Example 3: Search for "The"

```bash
curl "http://localhost:8000/api/books/?search=The"
```

**Result:** Books with "The" in title or author name

---

### Example 4: Filter + Search + Order (Complex Query)

```bash
curl "http://localhost:8000/api/books/?author_name=King&publication_year_min=1980&search=stand&ordering=title"
```

**What happens:**
1. Filter: author_name contains 'King'
2. Filter: publication_year >= 1980
3. Search: 'stand' in title or author
4. Order: alphabetically by title
5. Result: "The Stand" by Stephen King (if multiple matches)

---

### Example 5: Order Books Alphabetically (A-Z)

```bash
curl "http://localhost:8000/api/books/?ordering=title"
```

**Result:**
```json
{
    "count": 152,
    "results": [
        {"title": "1984"},
        {"title": "Foundation"},
        {"title": "Neuromancer"},
        ...
        {"title": "The Hobbit"}
    ]
}
```

---

### Example 6: Pagination with Ordering

```bash
# Page 1
curl "http://localhost:8000/api/books/?ordering=title&page=1"

# Page 2
curl "http://localhost:8000/api/books/?ordering=title&page=2"
```

**Result:** Books sorted alphabetically, paginated across pages

---

### Example 7: Books from 1950s, Newest First

```bash
curl "http://localhost:8000/api/books/?publication_year_min=1950&publication_year_max=1959&ordering=-publication_year"
```

**Result:** Books from 1950s, newest first in that range

---

### Example 8: Year Range Filter

```bash
curl "http://localhost:8000/api/books/?publication_year_min=1930&publication_year_max=1960"
```

**Result:** Classic books from 1930-1960, newest first (default ordering)

---

## Author API - Complete Query Examples

### Example 1: List All Authors (Alphabetical)

```bash
curl http://localhost:8000/api/authors/
```

**Response:**
```json
{
    "count": 42,
    "results": [
        {
            "id": 1,
            "name": "Asimov, Isaac",
            "books": [
                {"id": 5, "title": "Foundation", "publication_year": 1951},
                ...
            ]
        },
        ...
    ]
}
```

**Ordering:** Alphabetical by name (default)

---

### Example 2: Search for Author

```bash
curl "http://localhost:8000/api/authors/?search=King"
```

**Result:** Authors with "King" in name (e.g., "Stephen King", "King, Martin", etc.)

---

### Example 3: Authors Z-A (Reverse Order)

```bash
curl "http://localhost:8000/api/authors/?ordering=-name"
```

**Result:**
```
Tolkien, J.R.R.
Orwell, George
King, Stephen
Asimov, Isaac
```

---

### Example 4: Recently Added Authors

```bash
curl "http://localhost:8000/api/authors/?ordering=-id"
```

**Result:** Most recently added authors first

---

### Example 5: Get Specific Author with Books

```bash
curl http://localhost:8000/api/authors/1/
```

**Response:**
```json
{
    "id": 1,
    "name": "J.R.R. Tolkien",
    "books": [
        {
            "id": 1,
            "title": "The Hobbit",
            "publication_year": 1937
        },
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954
        },
        {
            "id": 31,
            "title": "The Silmarillion",
            "publication_year": 1977
        }
    ]
}
```

---

## Python Usage Examples

### Using Requests Library

```python
import requests

BASE_BOOKS = 'http://localhost:8000/api/books/'
BASE_AUTHORS = 'http://localhost:8000/api/authors/'

# Example 1: Get all books (newest first)
response = requests.get(BASE_BOOKS)
books = response.json()['results']
print(f"Total books: {response.json()['count']}")

# Example 2: Search for author
response = requests.get(BASE_BOOKS, params={'search': 'King'})
matches = response.json()['results']
print(f"Found {len(matches)} King-related books")

# Example 3: Filter by year range
response = requests.get(BASE_BOOKS, params={
    'publication_year_min': 1950,
    'publication_year_max': 1960,
    'ordering': 'publication_year'
})
classic_books = response.json()['results']

# Example 4: Complex query
response = requests.get(BASE_BOOKS, params={
    'search': 'The',
    'author_name': 'Tolkien',
    'publication_year_min': 1930,
    'ordering': 'publication_year'
})
tolkien_tomes = response.json()['results']

# Example 5: Authors paginated
response = requests.get(BASE_AUTHORS, params={
    'search': 'King',
    'ordering': 'name',
    'page': 1
})
king_authors = response.json()['results']
```

---

## Query Parameter Reference

### Book Endpoint Filters

```
?title=value                    - Filter by title (substring)
?author_name=value              - Filter by author name (substring)
?publication_year=1937          - Filter by exact year
?publication_year_min=1930      - Filter by minimum year (inclusive)
?publication_year_max=1960      - Filter by maximum year (inclusive)

?search=value                   - Search title and author name

?ordering=title                 - Sort A-Z by title
?ordering=-title                - Sort Z-A by title
?ordering=publication_year      - Sort oldest first
?ordering=-publication_year     - Sort newest first (DEFAULT)
?ordering=author__name          - Sort A-Z by author
?ordering=id                    - Sort by creation (first added)
?ordering=-id                   - Sort by creation (last added)

?page=1                         - First page (DEFAULT)
?page=2                         - Second page
```

---

### Author Endpoint Filters

```
?search=value                   - Search by author name

?ordering=name                  - Sort A-Z by name (DEFAULT)
?ordering=-name                 - Sort Z-A by name
?ordering=id                    - Sort by creation (first added)
?ordering=-id                   - Sort by creation (last added)

?page=1                         - First page
?page=2                         - Second page
```

---

## Common Workflows

### Workflow 1: Find a Book

```python
# User wants to find "The Lord of the Rings"
response = requests.get('http://localhost:8000/api/books/', 
    params={'search': 'Lord of the Rings'})
books = response.json()['results']
if books:
    print(f"Found: {books[0]['title']} by author {books[0]['author']}")
```

---

### Workflow 2: Browse Books by Author

```python
# First get author
author_response = requests.get('http://localhost:8000/api/authors/', 
    params={'search': 'Tolkien'})
authors = author_response.json()['results']

if authors:
    author = authors[0]
    print(f"Author: {author['name']}")
    print(f"Books by this author:")
    for book in author['books']:
        print(f"  - {book['title']} ({book['publication_year']})")
```

---

### Workflow 3: Find Latest Books in Genre

```python
# Get recently published books
response = requests.get('http://localhost:8000/api/books/', 
    params={
        'publication_year_min': 2000,
        'ordering': '-publication_year'
    })
recent_books = response.json()['results']
for book in recent_books[:5]:
    print(f"{book['title']} - {book['publication_year']}")
```

---

### Workflow 4: Create a Book (Requires Authentication)

```python
# Create an author first
author_data = {"name": "Stephen King"}
auth = ('username', 'password')  # HTTP Basic Auth
author_response = requests.post(
    'http://localhost:8000/api/authors/create/',
    json=author_data,
    auth=auth
)
author_id = author_response.json()['id']

# Now create a book
book_data = {
    "title": "The Stand",
    "publication_year": 1978,
    "author": author_id
}
book_response = requests.post(
    'http://localhost:8000/api/books/create/',
    json=book_data,
    auth=auth
)
print(f"Created book: {book_response.json()['title']}")
```

---

## API Contract Summary

### Request Format

```
GET /api/books/?[filters]&[search]&[ordering]&[pagination]

Where:
  [filters]    = Multiple filter parameters combined with &
  [search]     = ?search=term
  [ordering]   = ?ordering=[field]|-[field]
  [pagination] = ?page=N
```

### Response Format

```json
{
    "count": 152,           // Total number of results (not page count)
    "next": "...?page=2",   // URL to next page or null
    "previous": null,        // URL to previous page or null
    "results": [            // Array of result objects
        {
            "id": 1,
            "title": "...",
            "publication_year": 1937,
            "author": 1
        },
        ...
    ]
}
```

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET successful |
| 201 | Created | POST successful |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid filter field |
| 401 | Unauthorized | No authentication on protected endpoint |
| 404 | Not Found | Book/Author doesn't exist |
| 405 | Method Not Allowed | Using wrong HTTP method |

---

## Best Practices

### 1. Use Built-in Search First

```python
# Good - Let database handle search
requests.get(BASE_BOOKS, params={'search': 'King'})

# Bad - Fetching all then filtering in code
all_books = requests.get(BASE_BOOKS).json()['results']
king_books = [b for b in all_books if 'King' in b['title']]
```

---

### 2. Combine Filters for Efficiency

```python
# Good - Filter before paginating
requests.get(BASE_BOOKS, params={
    'author_name': 'King',
    'publication_year_min': 1980,
    'page': 1
})

# Less efficient - Multiple requests
req1 = requests.get(BASE_BOOKS, params={'author_name': 'King'})
req2 = requests.get(BASE_BOOKS, params={'publication_year_min': 1980})
```

---

### 3. Use Pagination for Large Results

```python
# Good - Paginated requests
page = 1
all_results = []
while True:
    response = requests.get(BASE_BOOKS, params={'page': page})
    data = response.json()
    all_results.extend(data['results'])
    if not data['next']:
        break
    page += 1

# Bad - Trying to get all results at once (will timeout)
response = requests.get(BASE_BOOKS)  # Might timeout with 1000+ results
```

---

### 4. Use Appropriate Ordering

```python
# Good - Index-supported ordering
?ordering=-publication_year  # Fast with index

# Less efficient - Complex ordering
?ordering=author__name  # Slower (requires JOIN)
```

---

## Performance Tips

### 1. Test with cURL First

```bash
# Simple debugging
curl "http://localhost:8000/api/books/?search=test"

# Pretty print JSON
curl -s "http://localhost:8000/api/books/?search=test" | python -m json.tool
```

---

### 2. Monitor Response Times

```python
import time

start = time.time()
response = requests.get('http://localhost:8000/api/books/?search=The&ordering=-publication_year')
duration = time.time() - start

print(f"Query took {duration*1000:.2f}ms")
print(f"Results: {response.json()['count']}")
```

---

### 3. Use Caching for Frequent Queries

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=100)
def get_authors():
    response = requests.get('http://localhost:8000/api/authors/')
    return response.json()['results']

# First call hits API
authors1 = get_authors()

# Second call returns cached results
authors2 = get_authors()
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty results on search | Check spelling, try shorter terms |
| 400 Bad Request on ordering | Use valid field: title, publication_year, author__name, id |
| 401 Unauthorized on POST | Add authentication credentials |
| Pagination URL seems long | Normal - includes all query params |
| Slow searches | Add indexes to database fields |

---

## Next Steps

- Deploy to production server
- Set up caching layer
- Monitor query performance
- Add more complex filtering options
- Implement search analytics

---

**Status:** ✅ STEP 4 COMPLETE  
**Date:** February 14, 2026  
**API Integration Version:** 1.0
