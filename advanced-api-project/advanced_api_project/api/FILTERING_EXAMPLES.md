# Book API - Filtering Examples and Use Cases

## Overview

This document provides practical examples of using the Book API's advanced filtering, searching, and ordering capabilities.

---

## Sample Data

Assuming the following books exist in the database:

| ID | Title | Year | Author |
|----|-------|------|--------|
| 1 | The Hobbit | 1937 | J.R.R. Tolkien |
| 2 | The Lord of the Rings | 1954 | J.R.R. Tolkien |
| 3 | The Silmarillion | 1977 | J.R.R. Tolkien |
| 4 | A Game of Thrones | 1996 | George R.R. Martin |
| 5 | Dune | 1965 | Frank Herbert |
| 6 | Foundation | 1951 | Isaac Asimov |
| 7 | 1984 | 1949 | George Orwell |
| 8 | The Shining | 1977 | Stephen King |
| 9 | IT | 1986 | Stephen King |
| 10 | The Stand | 1978 | Stephen King |

---

## Basic Filtering Examples

### 1. Filter by Title

**Query:** Find all books with "Ring" in the title

```
GET /api/books/?title=Ring
```

**Result:**
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

**Explanation:**
- Case-insensitive substring search in title
- "Ring" matches both "The Lord of the Rings" and by relevance "The Hobbit" (if using full-text search)

---

### 2. Filter by Author Name

**Query:** Find all books by Stephen King

```
GET /api/books/?author_name=King
```

**Result:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 9,
            "title": "IT",
            "publication_year": 1986,
            "author": 7
        },
        {
            "id": 10,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 7
        },
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        }
    ]
}
```

**Explanation:**
- Filters books where author name contains "King"
- Matches all three Stephen King books

---

### 3. Filter by Publication Year

**Query:** Find books published exactly in 1977

```
GET /api/books/?publication_year=1977
```

**Result:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 3,
            "title": "The Silmarillion",
            "publication_year": 1977,
            "author": 1
        },
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        }
    ]
}
```

---

### 4. Filter by Year Range - Minimum Year

**Query:** Find all books published in or after 1970

```
GET /api/books/?publication_year_min=1970
```

**Result:** Returns books from 1970 onwards (7 books)

---

### 5. Filter by Year Range - Maximum Year

**Query:** Find all books published before 1950

```
GET /api/books/?publication_year_max=1950
```

**Result:**
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
            "id": 7,
            "title": "1984",
            "publication_year": 1949,
            "author": 8
        },
        {
            "id": 6,
            "title": "Foundation",
            "publication_year": 1951,
            "author": 4
        }
    ]
}
```

**Note:** 1951 is included because `publication_year_max` uses <= (less than or equal)

---

### 6. Filter by Year Range - Both Min and Max

**Query:** Find books published between 1950 and 1980 (inclusive)

```
GET /api/books/?publication_year_min=1950&publication_year_max=1980
```

**Result:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 6,
            "title": "Foundation",
            "publication_year": 1951,
            "author": 4
        },
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        },
        {
            "id": 5,
            "title": "Dune",
            "publication_year": 1965,
            "author": 3
        },
        {
            "id": 3,
            "title": "The Silmarillion",
            "publication_year": 1977,
            "author": 1
        },
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        }
    ]
}
```

---

## Search Examples

### 7. Full-Text Search

**Query:** Search for "Lord"

```
GET /api/books/?search=Lord
```

**Result:**
```json
{
    "count": 1,
    "results": [
        {
            "id": 2,
            "title": "The Lord of the Rings",
            "publication_year": 1954,
            "author": 1
        }
    ]
}
```

**Explanation:**
- Searches in title and author name
- Finds "The **Lord** of the Rings"

---

### 8. Search for Author Name

**Query:** Search for "Tolkien"

```
GET /api/books/?search=Tolkien
```

**Result:**
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
            "id": 3,
            "title": "The Silmarillion",
            "publication_year": 1977,
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

**Explanation:**
- Finds all books by "Tolkien"
- Searches the author name field

---

### 9. Case-Insensitive Search

**Query:** Search for "king" (lowercase)

```
GET /api/books/?search=king
```

**Result:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        },
        {
            "id": 10,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 7
        },
        {
            "id": 9,
            "title": "IT",
            "publication_year": 1986,
            "author": 7
        }
    ]
}
```

**Explanation:**
- Case-insensitive search finds "Stephen **King**" books
- Also matches "IT" if "king" appears in it (case-insensitive)

---

## Ordering Examples

### 10. Sort by Title (A-Z)

**Query:** Order books alphabetically by title

```
GET /api/books/?ordering=title
```

**Result:**
```json
{
    "count": 10,
    "results": [
        {"id": 7, "title": "1984", ...},
        {"id": 4, "title": "A Game of Thrones", ...},
        {"id": 6, "title": "Foundation", ...},
        {"id": 5, "title": "Dune", ...},
        {"id": 9, "title": "IT", ...},
        {"id": 1, "title": "The Hobbit", ...},
        {"id": 2, "title": "The Lord of the Rings", ...},
        {"id": 3, "title": "The Silmarillion", ...},
        {"id": 8, "title": "The Shining", ...},
        {"id": 10, "title": "The Stand", ...}
    ]
}
```

---

### 11. Sort by Title (Z-A, Reverse)

**Query:** Order books in reverse alphabetical order

```
GET /api/books/?ordering=-title
```

**Result:** Reverse order of example 10

---

### 12. Sort by Publication Year (Oldest First)

**Query:** Order books by publication year, oldest first

```
GET /api/books/?ordering=publication_year
```

**Result:**
```json
{
    "count": 10,
    "results": [
        {"id": 1, "title": "The Hobbit", "publication_year": 1937, ...},
        {"id": 7, "title": "1984", "publication_year": 1949, ...},
        {"id": 6, "title": "Foundation", "publication_year": 1951, ...},
        {"id": 2, "title": "The Lord of the Rings", "publication_year": 1954, ...},
        {"id": 5, "title": "Dune", "publication_year": 1965, ...},
        {"id": 3, "title": "The Silmarillion", "publication_year": 1977, ...},
        {"id": 8, "title": "The Shining", "publication_year": 1977, ...},
        {"id": 10, "title": "The Stand", "publication_year": 1978, ...},
        {"id": 4, "title": "A Game of Thrones", "publication_year": 1996, ...},
        {"id": 9, "title": "IT", "publication_year": 1986, ...}
    ]
}
```

---

### 13. Sort by Publication Year (Newest First - Default)

**Query:** Default order (no parameter needed)

```
GET /api/books/
```

Or explicitly:

```
GET /api/books/?ordering=-publication_year
```

**Result:** Newest books first (reverse of example 12)

---

### 14. Sort by Author Name (A-Z)

**Query:** Order books by author name alphabetically

```
GET /api/books/?ordering=author__name
```

**Result:**
```json
{
    "count": 10,
    "results": [
        {"id": 6, "title": "Foundation", "author": {"id": 4, "name": "Isaac Asimov"}},
        {"id": 1, "title": "The Hobbit", "author": {"id": 1, "name": "J.R.R. Tolkien"}},
        {"id": 2, "title": "The Lord of the Rings", "author": {"id": 1, "name": "J.R.R. Tolkien"}},
        {"id": 3, "title": "The Silmarillion", "author": {"id": 1, "name": "J.R.R. Tolkien"}},
        {"id": 4, "title": "A Game of Thrones", "author": {"id": 2, "name": "George R.R. Martin"}},
        {"id": 7, "title": "1984", "author": {"id": 8, "name": "George Orwell"}},
        {"id": 8, "title": "The Shining", "author": {"id": 7, "name": "Stephen King"}},
        {"id": 9, "title": "IT", "author": {"id": 7, "name": "Stephen King"}},
        {"id": 10, "title": "The Stand", "author": {"id": 7, "name": "Stephen King"}},
        {"id": 5, "title": "Dune", "author": {"id": 3, "name": "Frank Herbert"}}
    ]
}
```

---

## Combined Query Examples

### 15. Filter + Search

**Query:** Find books by King that match "The"

```
GET /api/books/?author_name=King&search=The
```

**Result:**
```json
{
    "count": 2,
    "results": [
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        },
        {
            "id": 10,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 7
        }
    ]
}
```

---

### 16. Filter + Ordering

**Query:** Find Tolkien's books in publication order (oldest first)

```
GET /api/books/?author_name=Tolkien&ordering=publication_year
```

**Result:**
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
            "title": "The Silmarillion",
            "publication_year": 1977,
            "author": 1
        }
    ]
}
```

---

### 17. Year Range + Ordering + Author Filter

**Query:** Find books by King published between 1970 and 1990, newest first

```
GET /api/books/?author_name=King&publication_year_min=1970&publication_year_max=1990&ordering=-publication_year
```

**Result:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 9,
            "title": "IT",
            "publication_year": 1986,
            "author": 7
        },
        {
            "id": 10,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 7
        },
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        }
    ]
}
```

---

### 18. Complex Query: Title + Year Range + Ordering

**Query:** Find books with "The" in title, published between 1940 and 1980, ordered by publication year

```
GET /api/books/?title=The&publication_year_min=1940&publication_year_max=1980&ordering=publication_year
```

**Result:**
```json
{
    "count": 4,
    "results": [
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
        },
        {
            "id": 8,
            "title": "The Shining",
            "publication_year": 1977,
            "author": 7
        },
        {
            "id": 10,
            "title": "The Stand",
            "publication_year": 1978,
            "author": 7
        }
    ]
}
```

---

## Practical Use Cases

### Use Case 1: Browse Popular Classic Sci-Fi

**Query:** Find science fiction books published before 1980, ordered oldest first

```
GET /api/books/?publication_year_max=1980&ordering=publication_year
```

**Use Case:** Curating a "Classic Sci-Fi" collection

---

### Use Case 2: Find All Works by an Author

**Query:** Find all books by George R.R. Martin

```
GET /api/books/?author_name=Martin
```

**Use Case:** User wants to see an author's bibliography

---

### Use Case 3: Search for a Book

**Query:** Search for "rings"

```
GET /api/books/?search=rings
```

**Use Case:** User searches for a specific book

---

### Use Case 4: Browse by Era

**Query:** Find books published in the 1950s

```
GET /api/books/?publication_year_min=1950&publication_year_max=1959&ordering=publication_year
```

**Use Case:** User wants books from a specific decade

---

### Use Case 5: Find Recent Works by Classic Author

**Query:** Find Tolkien's books published after 1950

```
GET /api/books/?author_name=Tolkien&publication_year_min=1950
```

**Use Case:** User wants Tolkien's later works

---

### Use Case 6: Alphabetical Browse with Filters

**Query:** List all books by Stephen King, sorted A-Z

```
GET /api/books/?author_name=King&ordering=title
```

**Use Case:** User browses an author's body of work alphabetically

---

## Pagination with Filters

All filtered results are paginated (default 10 books per page):

```
GET /api/books/?author_name=King&page=1
```

Response:
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [...]
}
```

Fields in paginated response:
- `count`: Total number of results (across all pages)
- `next`: URL to next page (if exists)
- `previous`: URL to previous page (if exists)
- `results`: Array of book objects for current page

---

## Error Handling Examples

### Invalid Ordering Field

**Query:**
```
GET /api/books/?ordering=invalid_field
```

**Response (400 Bad Request):**
```json
{
    "detail": "Invalid ordering field: invalid_field"
}
```

---

### Invalid Year (Non-Numeric)

**Query:**
```
GET /api/books/?publication_year_min=abc
```

**Response:** Filter is silently ignored, returns all/default results

---

## Performance Tips

1. **Use specific filters** instead of search when possible
   - `?author_name=King` is faster than `?search=King`

2. **Combine filters** for better results
   - `?author_name=King&publication_year_min=1980` narrows down results

3. **Use pagination** for large result sets
   - Default page size: 10 books
   - Reduces data transfer

4. **Cache read requests** if possible
   - GET requests can be safely cached

---

## Related Links

- [API Documentation](VIEWS_DOCUMENTATION.md)
- [Advanced Filtering Guide](ADVANCED_FILTERING_GUIDE.md)
- [Setup Guide](FILTERING_SETUP.md)
