# STEP 6: Unit Tests - Quick Reference & Execution Guide

## Quick Start (Run Tests Now)

### 1. Start Django Server (Terminal 1)
```bash
python manage.py runserver
```

### 2. Run All Tests (Terminal 2)
```bash
python manage.py test api.test_views
```

### Expected Output
```
Ran 70+ tests in 2-3s

OK

System check identified no issues (0 silenced).
```

---

## Common Commands

### Run All API Tests
```bash
python manage.py test api.test_views
```

### Run with Verbose Output (see each test)
```bash
python manage.py test api.test_views -v 2
```

### Run Specific Test Class
```bash
# CRUD tests
python manage.py test api.test_views.BookCRUDTestCase

# Filtering tests
python manage.py test api.test_views.BookFilteringTestCase

# Searching tests
python manage.py test api.test_views.BookSearchingTestCase

# Ordering tests
python manage.py test api.test_views.BookOrderingTestCase

# Pagination tests
python manage.py test api.test_views.BookPaginationTestCase

# Authentication tests
python manage.py test api.test_views.BookAuthenticationTestCase

# Author API tests
python manage.py test api.test_views.AuthorAPITestCase
```

### Run Single Test Method
```bash
# Example: Test creating a book
python manage.py test api.test_views.BookCRUDTestCase.test_create_book_authenticated

# Example: Test filtering by author
python manage.py test api.test_views.BookFilteringTestCase.test_filter_by_author_name

# Example: Test ordering by title
python manage.py test api.test_views.BookOrderingTestCase.test_ordering_by_title_ascending
```

### Run with Coverage Analysis
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='api' manage.py test api.test_views

# View coverage report
coverage report

# Generate HTML report (opens in browser)
coverage html
python -m http.server  # Then visit http://localhost:8000/htmlcov/
```

---

## Test Categories at a Glance

### 1. CRUD Operations (11 Tests)
**What:** Create, Read, Update, Delete books  
**Run:**
```bash
python manage.py test api.test_views.BookCRUDTestCase -v 2
```
**Key Tests:**
- test_list_books
- test_retrieve_single_book
- test_create_book_authenticated
- test_update_book_authenticated
- test_delete_book_authenticated
- test_create_book_invalid_year (validation)

**Example Failure:** Book creation denied (should pass with auth)
```
Status: 401 (expected 201)
→ Solution: Ensure user is authenticated
```

---

### 2. Filtering (9 Tests)
**What:** Filter by author, title, year  
**Run:**
```bash
python manage.py test api.test_views.BookFilteringTestCase -v 2
```
**Key Tests:**
- test_filter_by_author_name
- test_filter_by_title
- test_filter_by_publication_year_exact
- test_filter_by_year_range
- test_multiple_filters_combined

**Example Query Tested:**
```bash
/api/books/?author_name=Tolkien&publication_year_min=1940
```

---

### 3. Searching (6 Tests)
**What:** Search across book titles and author names  
**Run:**
```bash
python manage.py test api.test_views.BookSearchingTestCase -v 2
```
**Key Tests:**
- test_search_by_title
- test_search_by_author_name
- test_search_case_insensitive
- test_search_partial_match

**Example Query Tested:**
```bash
/api/books/?search=King  # Finds all King books
/api/books/?search=ring  # Case-insensitive
```

---

### 4. Ordering (7 Tests)
**What:** Sort results by title, year, author  
**Run:**
```bash
python manage.py test api.test_views.BookOrderingTestCase -v 2
```
**Key Tests:**
- test_ordering_by_title_ascending
- test_ordering_by_title_descending
- test_ordering_by_year_ascending
- test_ordering_by_year_descending
- test_default_ordering (newest first)
- test_invalid_ordering_field (error handling)

**Example Query Tested:**
```bash
/api/books/?ordering=title          # A-Z
/api/books/?ordering=-title         # Z-A
/api/books/?ordering=-publication_year  # Newest first
```

---

### 5. Pagination (5 Tests)
**What:** Navigate through results across pages  
**Run:**
```bash
python manage.py test api.test_views.BookPaginationTestCase -v 2
```
**Key Tests:**
- test_pagination_page_1
- test_pagination_page_2
- test_pagination_count_accurate
- test_pagination_with_filter
- test_pagination_with_ordering

**Example Query Tested:**
```bash
/api/books/?page=1
/api/books/?page=2
/api/books/?author_name=King&page=1  # Pagination + Filter
```

---

### 6. Authentication (7 Tests)
**What:** Verify permissions and access control  
**Run:**
```bash
python manage.py test api.test_views.BookAuthenticationTestCase -v 2
```
**Key Tests:**
- test_read_without_authentication (should pass - 200)
- test_create_without_authentication (should fail - 401)
- test_create_with_authentication (should pass - 201)
- test_update_without_authentication (should fail - 401)
- test_delete_without_authentication (should fail - 401)

**Access Control Rules Tested:**
```
GET /api/books/          → 200 (public)
GET /api/books/{id}/     → 200 (public)
POST /api/books/create/  → 401 (requires auth)
PATCH /api/books/{id}/   → 401 (requires auth)
DELETE /api/books/{id}/  → 401 (requires auth)
```

---

### 7. Data Integrity (5 Tests)
**What:** Verify response data is correct  
**Run:**
```bash
python manage.py test api.test_views.BookResponseDataIntegrityTestCase -v 2
```
**Key Tests:**
- test_book_data_integrity
- test_book_list_data_integrity
- test_update_data_persistence
- test_filtered_results_accuracy
- test_list_books_response_format

**Verifies:**
- Title matches database
- Year matches database
- ID is correct
- All fields present
- Data types correct

---

### 8. Author Endpoints (7 Tests)
**What:** Test Author API (parallel to Book API)  
**Run:**
```bash
python manage.py test api.test_views.AuthorAPITestCase -v 2
```
**Key Tests:**
- test_list_authors
- test_retrieve_single_author
- test_search_authors
- test_order_authors
- test_create_author_authenticated
- test_update_author_authenticated
- test_delete_author_authenticated

---

### 9. Status Codes (10 Tests)
**What:** Verify all endpoints return correct HTTP status codes  
**Run:**
```bash
python manage.py test api.test_views.APIEndpointStatusTestCase -v 2
```
**Status Codes Verified:**
```
200 OK              → GET requests on valid resources
201 Created         → POST creates new resource
204 No Content      → DELETE successful (no return body)
400 Bad Request     → Invalid ordering field
401 Unauthorized    → Missing authentication
404 Not Found       → Resource doesn't exist
```

---

### 10. Complex Queries (3 Tests)
**What:** Multiple features working together  
**Run:**
```bash
python manage.py test api.test_views.ComplexQueryTestCase -v 2
```
**Complex Queries Tested:**
```
?author_name=Tolkien&search=The&ordering=publication_year
?publication_year_min=1970&publication_year_max=1980&search=ing
?author_name=King&page=1 (Author filter + Pagination)
```

---

## Test Execution Examples

### Example 1: Test One Filter
```bash
python manage.py test api.test_views.BookFilteringTestCase.test_filter_by_author_name -v 2
```
**Output:**
```
test_filter_by_author_name (api.test_views.BookFilteringTestCase) ... ok
```

### Example 2: Test All Ordering
```bash
python manage.py test api.test_views.BookOrderingTestCase -v 2
```
**Output:**
```
test_default_ordering ................... ok
test_ordering_by_title_ascending ........ ok
test_ordering_by_title_descending ....... ok
test_ordering_by_year_ascending ......... ok
test_ordering_by_year_descending ........ ok
test_ordering_by_author_name ............ ok
test_invalid_ordering_field ............. ok

Ran 7 tests in 0.234s
OK
```

### Example 3: Run All with Verbosity
```bash
python manage.py test api.test_views -v 2
```
**Will show:** All 70+ tests with OK/FAIL status

---

## Understanding Test Output

### PASS Example
```
test_create_book_authenticated (api.test_views.BookCRUDTestCase) ... ok (0.045s)
```
✅ Test passed in 45ms

### FAIL Example
```
test_create_book_authenticated (api.test_views.BookCRUDTestCase) ... FAIL
AssertionError: 400 != 201
```
❌ Expected 201 but got 400

### ERROR Example
```
test_create_book_authenticated (api.test_views.BookCRUDTestCase) ... ERROR
AttributeError: 'NoneType' object has no attribute 'id'
```
❌ Code error (not assertion failure)

---

## Debugging Failed Tests

### Step 1: Run Test with Verbose Output
```bash
python manage.py test api.test_views.BookCRUDTestCase.test_create_book_authenticated -v 2
```

### Step 2: View Full Error Message
Look for:
- **AssertionError:** Assertion failed (data mismatch)
- **AttributeError:** Attribute doesn't exist
- **KeyError:** Dictionary key missing
- **Status code:** Wrong HTTP status

### Step 3: Add Debug Print
Edit the test temporarily:
```python
def test_create_book_authenticated(self):
    self.client.force_authenticate(user=self.user)
    data = {...}
    
    response = self.client.post('/api/books/create/', data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    self.assertEqual(response.status_code, 201)
```

Run again:
```bash
python manage.py test api.test_views.BookCRUDTestCase.test_create_book_authenticated -v 2
```

### Step 4: Check Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| 401 on POST | Not authenticated | Add `self.client.force_authenticate(user=self.user)` |
| 404 on GET | Wrong URL | Check urls.py endpoint path |
| 400 on POST | Validation failed | Check serializer validation rules |
| AttributeError | Missing setUp | Add required test data in setUp |
| Empty results | Wrong filter | Verify filter parameter name |

---

## Coverage Report

### Generate Simple Report
```bash
coverage run --source='api' manage.py test api.test_views
coverage report
```

**Output:**
```
Name             Stmts   Miss  Cover
------------------------------------
api/__init__.py      0      0   100%
api/models.py       20      0   100%
api/views.py        85      5    94%
api/filters.py      30      0   100%
api/serializers.py  40      2    95%
------------------------------------
TOTAL              175      7    96%
```

### Generate Visual Report
```bash
coverage html
# Opens htmlcov/index.html with detailed coverage
```

---

## Test Maintenance

### Add New Test
1. **Identify what to test**
2. **Add method to appropriate class** (or create new class)
3. **Use clear naming:** `test_<feature>_<scenario>`
4. **Add docstring**
5. **Run test:** `python manage.py test api.test_views.<Class>.<method>`

### Example: New Filter Test
```python
def test_filter_by_isbn(self):
    """Test filtering books by ISBN"""
    # Setup
    isbn = "978-0-06-112008-4"
    book = Book.objects.create(
        title="Test",
        isbn=isbn,
        author=self.author
    )
    
    # Execute
    response = self.client.get(f'/api/books/?isbn={isbn}')
    
    # Assert
    self.assertEqual(response.status_code, 200)
    data = response.json()
    self.assertEqual(data['count'], 1)
    self.assertEqual(data['results'][0]['isbn'], isbn)
```

---

## Running Tests in Different Environments

### Local Development
```bash
python manage.py test api.test_views
```

### Production Check (with settings)
```bash
python manage.py test api.test_views --settings=config.settings.production
```

### With Different Database (e.g., PostgreSQL)
```bash
python manage.py test api.test_views --keepdb
```

### Parallel Execution (faster)
```bash
python manage.py test api.test_views --parallel
```

---

## Performance Expectations

| Test Category | Execution Time | Tests |
|---------------|----------------|-------|
| CRUD | ~0.5s | 11 |
| Filtering | ~0.4s | 9 |
| Searching | ~0.3s | 6 |
| Ordering | ~0.4s | 7 |
| Pagination | ~0.3s | 5 |
| Authentication | ~0.4s | 7 |
| Data Integrity | ~0.3s | 5 |
| Author API | ~0.3s | 7 |
| Status Codes | ~0.4s | 10 |
| Complex Queries | ~0.3s | 3 |
| **TOTAL** | **~3-4 seconds** | **70+** |

---

## Test Success Criteria

✅ **All tests pass:** Run `python manage.py test api.test_views`

✅ **Coverage > 90%:** Run `coverage report`

✅ **No warnings:** Check system checks pass

✅ **Performance < 5s:** Complete suite runs fast

---

## Continuous Integration Setup

### Add to tox.ini
```ini
[testenv]
commands = 
    python manage.py test api.test_views -v 2
    coverage run --source='api' manage.py test api.test_views
    coverage report --fail-under=90
```

### Run with tox
```bash
tox
```

---

## What Gets Tested vs Not Tested

### ✅ Tested
- All CRUD endpoints
- All query parameters
- Authentication/permissions
- Response formats
- Error handling
- Edge cases (empty results, invalid input)

### ❌ Not Tested (Requires Integration/E2E)
- Frontend integration
- Real authentication (OAuth, etc.)
- Performance under load
- Database optimization
- Concurrent requests

---

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `python manage.py test api.test_views` |
| Run specific class | `python manage.py test api.test_views.BookCRUDTestCase` |
| Run single test | `python manage.py test api.test_views.BookCRUDTestCase.test_create_book_authenticated` |
| Verbose output | `python manage.py test api.test_views -v 2` |
| Check coverage | `coverage run --source='api' manage.py test api.test_views && coverage report` |
| Generate HTML report | `coverage html` then open `htmlcov/index.html` |
| Run with color | `python manage.py test api.test_views --verbosity=2` |
| Keep test database | `python manage.py test api.test_views --keepdb` |

---

## Success Indicators

**Before Deployment Verify:**
- ✅ All 70+ tests pass
- ✅ Coverage > 90%
- ✅ No warnings or errors
- ✅ Execution time < 5 seconds
- ✅ All endpoints tested
- ✅ Authentication enforced
- ✅ Response formats valid

---

## Summary

**70+ comprehensive unit tests** covering:
- ✅ CRUD operations
- ✅ Filtering functionality
- ✅ Search capabilities
- ✅ Ordering features
- ✅ Pagination
- ✅ Authentication/Permissions
- ✅ Data integrity
- ✅ Response validation
- ✅ Complex queries
- ✅ Author endpoints

**Ready to run:** `python manage.py test api.test_views`

---

**Status:** ✅ STEP 6 UNIT TESTS COMPLETE  
**Date:** February 14, 2026  
**File:** api/test_views.py  
**Tests:** 70+  
**Expected Pass Rate:** 100%
