# Advanced Query Capabilities - API Documentation

This document describes the advanced filtering, searching, and ordering features available in the Book API.

## Overview

The Book API (`/api/books/`) provides three powerful query capabilities:
1. **Filtering** - Filter results by specific field values
2. **Searching** - Text search across multiple fields
3. **Ordering** - Sort results by specified fields

## 1. Filtering

### Available Filters

#### Basic Filters
- `title` - Filter by book title (case-insensitive, contains)
- `author` - Filter by author ID (exact match)
- `author_name` - Filter by author name (case-insensitive, contains)
- `publication_year` - Filter by exact publication year

#### Range Filters
- `publication_year_min` - Books published from this year onwards
- `publication_year_max` - Books published up to this year

### Filtering Examples

```bash
# Books with "django" in the title
GET /api/books/?title=django

# Books by author with ID 1
GET /api/books/?author=1

# Books by authors with "smith" in their name
GET /api/books/?author_name=smith

# Books published in 2024
GET /api/books/?publication_year=2024

# Books published from 2020 onwards
GET /api/books/?publication_year_min=2020

# Books published up to 2023
GET /api/books/?publication_year_max=2023

# Books published between 2020 and 2024
GET /api/books/?publication_year_min=2020&publication_year_max=2024
```

### Multiple Filters

You can combine multiple filters:

```bash
# Books by "Smith" published after 2020
GET /api/books/?author_name=smith&publication_year_min=2020
```

## 2. Search Functionality

### Search Configuration

The search functionality performs text-based searches across:
- Book title
- Author name

### How Search Works
- **Case-insensitive** - Searches ignore case differences
- **Partial matching** - Finds partial matches within the text
- **Multiple fields** - Searches across both title and author name simultaneously

### Search Examples

```bash
# Find books with "python" in title or author name
GET /api/books/?search=python

# Find books related to "django"
GET /api/books/?search=django

# Search for author name
GET /api/books/?search=jane

# Search with multiple terms (space-separated)
GET /api/books/?search=django rest
```

### Search vs. Filter

**Use Search when:**
- You want to find text across multiple fields
- You need fuzzy/partial matching
- You're building a general search feature

**Use Filter when:**
- You need exact field matching
- You're building faceted search
- You need range queries

## 3. Ordering (Sorting)

### Available Ordering Fields

- `title` - Sort by book title
- `publication_year` - Sort by publication year

### Ordering Direction

- **Ascending** (A-Z, oldest-newest): Use field name directly
- **Descending** (Z-A, newest-oldest): Prefix field name with `-`

### Ordering Examples

```bash
# Sort by title (A to Z)
GET /api/books/?ordering=title

# Sort by title (Z to A)
GET /api/books/?ordering=-title

# Sort by publication year (oldest first)
GET /api/books/?ordering=publication_year

# Sort by publication year (newest first)
GET /api/books/?ordering=-publication_year
```

### Default Ordering

If no ordering parameter is provided, results are sorted by `title` in ascending order.

## 4. Combined Queries

You can combine filtering, searching, and ordering in a single request:

```bash
# Books by "Smith", ordered by year (newest first)
GET /api/books/?author_name=smith&ordering=-publication_year

# Search for "python", show only recent books
GET /api/books/?search=python&publication_year_min=2020

# Books from 2020-2024 with "django" in title, sorted by year
GET /api/books/?title=django&publication_year_min=2020&publication_year_max=2024&ordering=publication_year

# Complete example: search, filter, and order
GET /api/books/?search=programming&publication_year_min=2020&ordering=-publication_year
```

## 5. Pagination

Results are automatically paginated:
- **Default page size**: 10 items per page
- **Access pages**: Use `?page=2` parameter

### Pagination Examples

```bash
# First page (default)
GET /api/books/

# Second page
GET /api/books/?page=2

# Combine with filtering
GET /api/books/?author_name=smith&page=2

# Combine with search and ordering
GET /api/books/?search=python&ordering=-publication_year&page=2
```

## 6. Response Format

All responses follow this structure:

```json
{
    "count": 25,
    "next": "http://api.example.com/api/books/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Django for Beginners",
            "publication_year": 2024,
            "author": 1
        },
        // ... more books
    ]
}
```

## 7. Permission Requirements

- **List/Read Operations**: Open to all users (authenticated or not)
- **Create/Update/Delete**: Requires authentication

## 8. Testing with cURL

### Filter by title
```bash
curl "http://localhost:8000/api/books/?title=django"
```

### Search
```bash
curl "http://localhost:8000/api/books/?search=python"
```

### Order by publication year (descending)
```bash
curl "http://localhost:8000/api/books/?ordering=-publication_year"
```

### Combined query
```bash
curl "http://localhost:8000/api/books/?author_name=smith&publication_year_min=2020&ordering=-publication_year"
```

## 9. Error Handling

### Invalid Filter Values
```bash
# Invalid year format
GET /api/books/?publication_year=invalid
# Returns: 400 Bad Request with error details
```

### Invalid Ordering Fields
```bash
# Non-existent field
GET /api/books/?ordering=invalid_field
# Silently ignores invalid field, uses default ordering
```

## 10. Best Practices

1. **Use specific filters over search** when you know the exact field
2. **Combine filters** to narrow down results effectively
3. **Use pagination** to improve performance with large datasets
4. **Cache frequently used queries** on the client side
5. **Use ordering** to provide better UX with sorted results

## Implementation Details

### Backend Components

- **DjangoFilterBackend**: Handles field-specific filtering
- **SearchFilter**: Manages text search across multiple fields
- **OrderingFilter**: Provides sorting capabilities

### Custom Filter Class

Location: `api/filters.py`

The `BookFilter` class provides advanced filtering options including:
- Case-insensitive text matching
- Range queries for publication year
- Cross-model filtering (author name)

## Support

For issues or questions about the API, please refer to the main API documentation or contact the development team.
