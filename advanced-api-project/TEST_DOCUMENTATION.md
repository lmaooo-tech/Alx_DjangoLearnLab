# API Unit Tests Documentation

## Overview

Comprehensive unit tests have been created for the advanced-api-project API endpoints in `/api/test_views.py`. These tests verify the functionality, data integrity, and access control of all CRUD operations.

## Test Coverage

### 1. CRUD Operations Tests

#### BookListViewTests
- ✅ List books (unauthenticated access)
- ✅ List books (authenticated access)
- ✅ Verify correct data structure in responses

#### BookDetailViewTests
- ✅ Retrieve single book (unauthenticated)
- ✅ Retrieve single book (authenticated)
- ✅ Handle non-existent books (404)
- ✅ Verify returned data fields

#### BookCreateViewTests
- ✅ Block creation for unauthenticated users (403)
- ✅ Allow creation for authenticated users (201)
- ✅ Validate future publication year (400)
- ✅ Validate required fields
- ✅ Validate author foreign key

#### BookUpdateViewTests
- ✅ Block updates for unauthenticated users (403)
- ✅ Allow updates for authenticated users (200)
- ✅ Support partial updates (PATCH)
- ✅ Handle non-existent books (404)

#### BookDeleteViewTests
- ✅ Block deletion for unauthenticated users (403)
- ✅ Allow deletion for authenticated users (204)
- ✅ Verify data is actually deleted
- ✅ Handle non-existent books (404)

### 2. Filtering Tests (BookFilteringTests)

- ✅ Filter by title (case-insensitive, contains)
- ✅ Filter by author ID (exact match)
- ✅ Filter by author name (case-insensitive)
- ✅ Filter by exact publication year
- ✅ Filter by minimum publication year
- ✅ Filter by maximum publication year
- ✅ Filter by year range (min and max combined)
- ✅ Apply multiple filters simultaneously

**Example Test Cases:**
```python
# Filter by title containing "django"
GET /api/books/?title=django

# Filter by author ID
GET /api/books/?author=1

# Filter by year range
GET /api/books/?publication_year_min=2020&publication_year_max=2023
```

### 3. Search Tests (BookSearchTests)

- ✅ Search by book title
- ✅ Search by author name
- ✅ Case-insensitive search
- ✅ Handle no results gracefully
- ✅ Search with multiple terms

**Example Test Cases:**
```python
# Search for "python" in title or author
GET /api/books/?search=python

# Case-insensitive search
GET /api/books/?search=DJANGO  # Same results as "django"
```

### 4. Ordering Tests (BookOrderingTests)

- ✅ Order by title (ascending)
- ✅ Order by title (descending)
- ✅ Order by publication year (ascending)
- ✅ Order by publication year (descending)
- ✅ Verify default ordering (by title)

**Example Test Cases:**
```python
# Order by title A-Z
GET /api/books/?ordering=title

# Order by year (newest first)
GET /api/books/?ordering=-publication_year
```

### 5. Combined Query Tests (BookCombinedQueryTests)

- ✅ Filter + Search combination
- ✅ Filter + Ordering combination
- ✅ Search + Ordering combination
- ✅ Filter + Search + Ordering (all three)

**Example Test Cases:**
```python
# Combined: filter by author, search for term, order by year
GET /api/books/?author_name=smith&search=django&ordering=-publication_year
```

### 6. Permissions Tests (BookPermissionsTests)

- ✅ List endpoint accessible without authentication
- ✅ Detail endpoint accessible without authentication
- ✅ Create endpoint requires authentication (403 for anonymous)
- ✅ Update endpoint requires authentication (403 for anonymous)
- ✅ Delete endpoint requires authentication (403 for anonymous)
- ✅ Authenticated users can create books
- ✅ Authenticated users can update books
- ✅ Authenticated users can delete books

### 7. Pagination Tests (BookPaginationTests)

- ✅ Response includes pagination metadata (count, next, previous, results)
- ✅ Pagination count is accurate

### 8. Validation Tests (BookValidationTests)

- ✅ Current year is valid for publication_year
- ✅ Past years are valid for publication_year
- ✅ Future years are rejected (400)
- ✅ Required fields are validated
- ✅ Error messages are meaningful

## Test Statistics

- **Total Test Cases**: 55 tests
- **Test Classes**: 11 classes
- **Coverage Areas**: 
  - CRUD operations (5 operations)
  - Filtering (8 test scenarios)
  - Searching (5 test scenarios)
  - Ordering (5 test scenarios)
  - Combined queries (4 test scenarios)
  - Permissions (9 test scenarios)
  - Pagination (2 test scenarios)
  - Validation (4 test scenarios)

## Running the Tests

### Run All Tests
```bash
python manage.py test api.test_views
```

### Run Specific Test Class
```bash
python manage.py test api.test_views.BookListViewTests
python manage.py test api.test_views.BookFilteringTests
python manage.py test api.test_views.BookPermissionsTests
```

### Run Specific Test Method
```bash
python manage.py test api.test_views.BookListViewTests.test_list_books_unauthenticated
```

### Run with Verbosity
```bash
python manage.py test api.test_views --verbosity=2
```

### Run with Coverage Report (if coverage is installed)
```bash
coverage run --source='.' manage.py test api.test_views
coverage report
coverage html
```

## Test Data Setup

Each test class uses a common setup with:

**Test Users:**
- Regular user: `testuser` / `testpass123`
- Admin user: `adminuser` / `adminpass123`

**Test Authors:**
- John Smith
- Jane Doe
- Robert Johnson

**Test Books:**
- "Django for Beginners" (2020) by John Smith
- "Python Programming" (2019) by Jane Doe
- "Advanced Django" (2022) by John Smith
- "REST API Design" (2021) by Robert Johnson

## Expected Test Results

All 55 tests should pass with the following verification:

✅ **CRUD Operations**: Full create, read, update, delete functionality  
✅ **Filtering**: All filter types work correctly  
✅ **Searching**: Text search across multiple fields  
✅ **Ordering**: Ascending and descending sorts  
✅ **Permissions**: Proper authentication enforcement  
✅ **Validation**: Data integrity maintained  
✅ **Status Codes**: Correct HTTP responses

## Test Response Verification

Tests verify:
1. **Status Codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 403 Forbidden, 404 Not Found
2. **Response Data**: Correct fields and values returned
3. **Data Integrity**: Database state matches expectations
4. **Permissions**: Access control properly enforced
5. **Validation**: Invalid data is rejected with appropriate errors

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: python manage.py test api.test_views --verbosity=2
```

## Maintenance

When adding new features:
1. Add corresponding tests to appropriate test class
2. Ensure test coverage remains comprehensive
3. Update this documentation
4. Run full test suite before committing

## Troubleshooting

### Common Issues

**ImportError: No module named 'rest_framework'**
```bash
pip install djangorestframework
```

**Database errors**
```bash
python manage.py migrate
```

**Test failures after model changes**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py test api.test_views
```

## Best Practices Demonstrated

1. ✅ Separate test classes for different concerns
2. ✅ Clear, descriptive test names
3. ✅ Comprehensive docstrings
4. ✅ DRY principle with setUp method
5. ✅ Test both positive and negative cases
6. ✅ Test edge cases (404, validation errors)
7. ✅ Test authentication and permissions
8. ✅ Test data integrity after operations
9. ✅ Use appropriate assertions
10. ✅ Test actual API responses, not just models

## Next Steps

Consider adding:
- Integration tests for complex workflows
- Performance tests for large datasets
- Load testing for concurrent requests
- API documentation tests (schema validation)
- Additional edge case scenarios
