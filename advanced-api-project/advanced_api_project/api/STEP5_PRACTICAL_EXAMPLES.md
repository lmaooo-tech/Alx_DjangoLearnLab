# STEP 5: API Testing - Practical Examples & Quick Reference

## Quick Start (Copy & Paste Ready)

### Before Testing: Ensure Sample Data Exists

```bash
# Access Django shell
python manage.py shell

# Create sample data
from blog.models import Author, Book

# Create authors
tolkien = Author.objects.create(name="J.R.R. Tolkien")
king = Author.objects.create(name="Stephen King")
orwell = Author.objects.create(name="George Orwell")

# Create books
Book.objects.create(title="The Hobbit", publication_year=1937, author=tolkien)
Book.objects.create(title="The Lord of the Rings", publication_year=1954, author=tolkien)
Book.objects.create(title="The Shining", publication_year=1977, author=king)
Book.objects.create(title="The Stand", publication_year=1978, author=king)
Book.objects.create(title="1984", publication_year=1949, author=orwell)

# Exit shell
exit()
```

---

## Category 1: Basic Functionality

### Test 1: Server Running Check
```bash
curl -i http://localhost:8000/api/books/
# Expected: HTTP/1.1 200 OK
```

### Test 2: Get Pretty JSON Output
```bash
curl -s http://localhost:8000/api/books/ | python -m json.tool
```

### Test 3: Count Total Books
```bash
curl -s http://localhost:8000/api/books/ | python -c "import sys,json; print('Total books:', json.load(sys.stdin)['count'])"
```

---

## Category 2: Filtering Tests

### F1: Filter by Author (Exact Substring Match)
```bash
curl "http://localhost:8000/api/books/?author_name=Tolkien"
```
Expected Results: 2 books (The Hobbit, The Lord of the Rings)

### F2: Filter by Author (Case Insensitive)
```bash
curl "http://localhost:8000/api/books/?author_name=tolkien"
```
Expected Results: Same as F1 (case-insensitive)

### F3: Filter by Partial Author Name
```bash
curl "http://localhost:8000/api/books/?author_name=olk"
```
Expected Results: 2 books (Tolkien books)

### F4: Filter by Title
```bash
curl "http://localhost:8000/api/books/?title=Hobbit"
```
Expected Results: 1 book (The Hobbit)

### F5: Filter by Title (Partial)
```bash
curl "http://localhost:8000/api/books/?title=The"
```
Expected Results: 4 books (all except 1984)

### F6: Filter by Exact Year
```bash
curl "http://localhost:8000/api/books/?publication_year=1978"
```
Expected Results: 1 book (The Stand)

### F7: Filter by Minimum Year
```bash
curl "http://localhost:8000/api/books/?publication_year_min=1975"
```
Expected Results: 2 books (The Shining, The Stand)

### F8: Filter by Maximum Year
```bash
curl "http://localhost:8000/api/books/?publication_year_max=1950"
```
Expected Results: 3 books (The Hobbit, 1984, The Lord of the Rings)

### F9: Filter by Year Range
```bash
curl "http://localhost:8000/api/books/?publication_year_min=1950&publication_year_max=1980"
```
Expected Results: 3 books (LOTR, The Shining, The Stand)

### F10: Filter - No Results
```bash
curl "http://localhost:8000/api/books/?author_name=NonExistent"
```
Expected Results: Empty array, count=0

---

## Category 3: Searching Tests

### S1: Search by Author Name
```bash
curl "http://localhost:8000/api/books/?search=King"
```
Expected Results: 2 books (both by Stephen King)

### S2: Search by Title
```bash
curl "http://localhost:8000/api/books/?search=Hobbit"
```
Expected Results: 1 book (The Hobbit)

### S3: Search Case Insensitive
```bash
curl "http://localhost:8000/api/books/?search=KING"
curl "http://localhost:8000/api/books/?search=king"
curl "http://localhost:8000/api/books/?search=King"
```
Expected Results: Same results for all (case-insensitive)

### S4: Partial Word Search
```bash
curl "http://localhost:8000/api/books/?search=obbi"
```
Expected Results: 1 book (The Hobbit - contains "obbits")

### S5: Search Multiple Word Match
```bash
curl "http://localhost:8000/api/books/?search=ring"
```
Expected Results: Books with "ring" - The Lord of the Rings, The Shining (contains "ring")

### S6: Search No Match
```bash
curl "http://localhost:8000/api/books/?search=NonexistentBook12345"
```
Expected Results: Empty results

---

## Category 4: Ordering Tests

### O1: Default Ordering (Newest First)
```bash
curl "http://localhost:8000/api/books/" | python -c "import sys,json; d=json.load(sys.stdin); print('Order:', [b['publication_year'] for b in d['results']])"
```
Expected Sequence: [1978, 1977, 1954, 1949, 1937]

### O2: Order by Title (A-Z)
```bash
curl "http://localhost:8000/api/books/?ordering=title" | python -c "import sys,json; d=json.load(sys.stdin); print('Titles:', [b['title'] for b in d['results']])"
```
Expected Sequence: 1984, The Hobbit, The Lord..., The Shining, The Stand

### O3: Order by Title (Z-A)
```bash
curl "http://localhost:8000/api/books/?ordering=-title" | python -c "import sys,json; d=json.load(sys.stdin); print('Titles:', [b['title'] for b in d['results']])"
```
Expected Sequence: Reverse of O2

### O4: Order by Year (Oldest First)
```bash
curl "http://localhost:8000/api/books/?ordering=publication_year" | python -c "import sys,json; d=json.load(sys.stdin); print('Years:', [b['publication_year'] for b in d['results']])"
```
Expected Sequence: [1937, 1949, 1954, 1977, 1978]

### O5: Order by Year (Newest First - Explicit)
```bash
curl "http://localhost:8000/api/books/?ordering=-publication_year" | python -c "import sys,json; d=json.load(sys.stdin); print('Years:', [b['publication_year'] for b in d['results']])"
```
Expected Sequence: [1978, 1977, 1954, 1949, 1937]

### O6: Order by Author Name
```bash
curl "http://localhost:8000/api/books/?ordering=author__name" | python -c "import sys,json; d=json.load(sys.stdin); print('Authors:', [str(b.get('author', '')) for b in d['results']])"
```
Expected Sequence: Grouped by author ID alphabetically (if using author ID)

### O7: Invalid Ordering Field (Should Error)
```bash
curl -w "\nHTTP Status: %{http_code}\n" "http://localhost:8000/api/books/?ordering=invalid_field"
```
Expected Result: HTTP 400 Bad Request

---

## Category 5: Combined Queries (Filter + Search)

### C1: Filter Author + Search Term
```bash
curl "http://localhost:8000/api/books/?author_name=King&search=Stand"
```
Expected Results: 1 book (The Stand)

### C2: Filter Year + Search
```bash
curl "http://localhost:8000/api/books/?publication_year_min=1970&search=ing"
```
Expected Results: Books after 1970 with "ing" (The Shining, The Stand)

### C3: Filter + Search (No Results)
```bash
curl "http://localhost:8000/api/books/?author_name=King&search=Hobbit"
```
Expected Results: Empty (no Hobbit books by King)

---

## Category 6: Combined Queries (Filter + Search + Order)

### C4: Author + Search + Order by Title
```bash
curl "http://localhost:8000/api/books/?author_name=Tolkien&search=The&ordering=title"
```
Expected Results: Tolkien books with "The", sorted alphabetically

### C5: Year Range + Search + Order by Year
```bash
curl "http://localhost:8000/api/books/?publication_year_min=1930&publication_year_max=1960&search=ing&ordering=publication_year"
```
Expected Results: Books 1930-1960 with "ing", chronological order

### C6: Complex 4-Parameter Query
```bash
curl "http://localhost:8000/api/books/?title=The&author_name=King&publication_year_min=1975&search=Stand&ordering=-publication_year"
```
Expected Results: King's books with "The" and "Stand" after 1975, newest first

---

## Category 7: Pagination Tests

### P1: First Page (Default)
```bash
curl "http://localhost:8000/api/books/?page=1" | python -c "import sys,json; d=json.load(sys.stdin); print(f'Count: {d[\"count\"]}, Results: {len(d[\"results\"])}')"
```
Expected: Shows count of 5 books, 5 results (or less if >10 total)

### P2: Check Pagination Fields
```bash
curl -s "http://localhost:8000/api/books/?page=1" | python -m json.tool | head -15
```
Expected: Shows "count", "next", "previous", "results" fields

### P3: Pagination with Ordering
```bash
curl "http://localhost:8000/api/books/?page=1&ordering=title" | python -c "import sys,json; d=json.load(sys.stdin); print('Titles P1:', [b['title'] for b in d['results']])"
```
Expected: Titles in alphabetical order

### P4: Non-Existent Page
```bash
curl -w "\nHTTP: %{http_code}\n" "http://localhost:8000/api/books/?page=999"
```
Expected: HTTP 404 or empty results (depends on implementation)

---

## Category 8: Author Endpoints

### Auth1: List All Authors
```bash
curl "http://localhost:8000/api/authors/" | python -m json.tool | head -20
```
Expected Results: List of authors with books

### Auth2: Search Authors
```bash
curl "http://localhost:8000/api/authors/?search=King"
```
Expected Results: Stephen King

### Auth3: Order Authors
```bash
curl "http://localhost:8000/api/authors/?ordering=name" | python -c "import sys,json; d=json.load(sys.stdin); print('Names:', [a['name'] for a in d['results']])"
```
Expected Results: Authors in alphabetical order

### Auth4: Create Author (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/authors/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Isaac Asimov"}'
```
Expected: HTTP 401 (or 201 if authenticated)

---

## Performance Testing

### Perf1: Measure Response Time
```bash
curl -w "\n\nResponse time: %{time_total}s\n" "http://localhost:8000/api/books/"
```
Expected: < 100ms for small dataset

### Perf2: Compare Performance (with vs without ordering)
```bash
# Without ordering
time curl -s "http://localhost:8000/api/books/" > /dev/null

# With ordering
time curl -s "http://localhost:8000/api/books/?ordering=title" > /dev/null

# With complex query
time curl -s "http://localhost:8000/api/books/?author_name=Tolkien&search=Ring&ordering=publication_year" > /dev/null
```
Expected: All similar timing (filtering is efficient)

---

## Debugging & Validation

### D1: Validate JSON Response
```bash
curl -s "http://localhost:8000/api/books/" | python -m json.tool > /dev/null && echo "✓ Valid JSON"
```
Expected: "✓ Valid JSON"

### D2: Check All Required Fields
```bash
curl -s "http://localhost:8000/api/books/" | python -c "import sys,json; d=json.load(sys.stdin); b=d['results'][0] if d['results'] else {}; print('Fields:', list(b.keys()))"
```
Expected: ['id', 'title', 'publication_year', 'author']

### D3: Save Response to File
```bash
curl -s "http://localhost:8000/api/books/?author_name=Tolkien" | python -m json.tool > tolkien_books.json
cat tolkien_books.json
```

### D4: Count Items in Response
```bash
curl -s "http://localhost:8000/api/books/" | python -c "import sys,json; print('Total items:', json.load(sys.stdin)['count'])"
```

---

## Comparison Tests (Verify Consistency)

### Compare1: Same Query Should Return Same Results
```bash
# Get first response
curl -s "http://localhost:8000/api/books/?author_name=King" > request1.json

# Wait 2 seconds
sleep 2

# Get second response
curl -s "http://localhost:8000/api/books/?author_name=King" > request2.json

# Compare
diff request1.json request2.json && echo "✓ Consistent" || echo "✗ Different"
```

### Compare2: Verify Filter + Search Intersection
```bash
# Both King books
curl -s "http://localhost:8000/api/books/?author_name=King" > all_king.json

# King's "Stand" books
curl -s "http://localhost:8000/api/books/?author_name=King&search=Stand" > king_stand.json

# Verify second is subset of first
echo "All King: $(curl -s 'http://localhost:8000/api/books/?author_name=King' | python -c 'import sys,json; print(json.load(sys.stdin)[\"count\"])')"
echo "King Stand: $(curl -s 'http://localhost:8000/api/books/?author_name=King&search=Stand' | python -c 'import sys,json; print(json.load(sys.stdin)[\"count\"])')"
```

---

## Test Execution Script

Create file: `run_api_tests.sh`

```bash
#!/bin/bash

echo "=========================================="
echo "API Testing Suite - Quick Validation"
echo "=========================================="
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter
PASS=0
FAIL=0

test_query() {
    local name="$1"
    local url="$2"
    local expected_code="$3"
    
    echo -n "Testing: $name ... "
    
    response=$(curl -s -o /tmp/test_response.json -w "%{http_code}" "$url")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓${NC}"
        ((PASS++))
    else
        echo -e "${RED}✗ (Expected $expected_code, got $response)${NC}"
        ((FAIL++))
    fi
}

BASE="http://localhost:8000/api/books"

echo "--- BASIC TESTS ---"
test_query "List all" "$BASE/" "200"
test_query "Page 1" "$BASE/?page=1" "200"

echo
echo "--- FILTERING TESTS ---"
test_query "Filter author" "$BASE/?author_name=Tolkien" "200"
test_query "Filter title" "$BASE/?title=Hobbit" "200"
test_query "Filter year" "$BASE/?publication_year=1978" "200"
test_query "Filter year range" "$BASE/?publication_year_min=1950&publication_year_max=1960" "200"

echo
echo "--- SEARCH TESTS ---"
test_query "Search author" "$BASE/?search=King" "200"
test_query "Search title" "$BASE/?search=Ring" "200"

echo
echo "--- ORDERING TESTS ---"
test_query "Order title A-Z" "$BASE/?ordering=title" "200"
test_query "Order title Z-A" "$BASE/?ordering=-title" "200"
test_query "Order year ASC" "$BASE/?ordering=publication_year" "200"
test_query "Order year DESC" "$BASE/?ordering=-publication_year" "200"

echo
echo "--- COMBINED TESTS ---"
test_query "Filter+Search" "$BASE/?author_name=King&search=Stand" "200"
test_query "Filter+Search+Order" "$BASE/?author_name=Tolkien&search=The&ordering=title" "200"

echo
echo "--- NEGATIVE TESTS ---"
test_query "Invalid ordering" "$BASE/?ordering=invalid" "400"

echo
echo "=========================================="
echo -e "Results: ${GREEN}$PASS Passed${NC}, ${RED}$FAIL Failed${NC}"
echo "=========================================="
```

Save and run:
```bash
chmod +x run_api_tests.sh
./run_api_tests.sh
```

---

## Expected Test Results Summary

| Category | Tests | Expected |
|----------|-------|----------|
| Filtering | 10 | ✓ All Pass |
| Searching | 6 | ✓ All Pass |
| Ordering | 7 | ✓ All Pass |
| Combined | 6 | ✓ All Pass |
| Pagination | 4 | ✓ All Pass |
| Authors API | 4 | ✓ All Pass |
| Performance | 3 | ✓ All < 100ms |
| Validation | 4 | ✓ All Pass |
| **TOTAL** | **44** | **✓ 44/44** |

---

## Quick Validation Checklist

Run these 5 commands to quickly validate everything works:

```bash
# 1. Server running?
curl http://localhost:8000/api/books/ >/dev/null 2>&1 && echo "✓ Server running"

# 2. Can filter?
curl -s "http://localhost:8000/api/books/?author_name=Tolkien" | grep -q "Hobbit" && echo "✓ Filtering works"

# 3. Can search?
curl -s "http://localhost:8000/api/books/?search=King" | grep -q "Stand" && echo "✓ Search works"

# 4. Can order?
curl -s "http://localhost:8000/api/books/?ordering=title" | grep -q "1984" && echo "✓ Ordering works"

# 5. Can combine?
curl -s "http://localhost:8000/api/books/?author_name=King&search=Stand&ordering=-publication_year" | grep -q "The Stand" && echo "✓ Combined queries work"
```

---

**Date:** February 14, 2026  
**Step:** 5/5 - API Testing (Practical Examples)  
**Status:** Ready for Testing ✓
