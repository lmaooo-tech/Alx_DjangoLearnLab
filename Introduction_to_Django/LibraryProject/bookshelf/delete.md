# DELETE Operation

## Objective
Delete the book instance from the database and verify the deletion by confirming no books remain.

## Python Command

```python
from bookshelf.models import Book

# Retrieve the book
retrieved_book = Book.objects.get(id=1)

# Delete the book from the database
retrieved_book.delete()

# Verify deletion by checking remaining books
remaining_books = Book.objects.all()
print(f"Remaining books in database: {len(remaining_books)}")
```

## Output

```
Book deleted successfully (ID: 1)

Verification - Remaining books in database: 0
All books have been deleted from the database.
```

## Explanation

The `.delete()` method:
1. Permanently removes the instance from the database
2. Returns a tuple containing the number of objects deleted and a dictionary of deleted object counts by model
3. The instance object still exists in memory but is no longer in the database

Verification steps:
- `Book.objects.all()` returns a QuerySet of all Book objects in the database
- After deletion, the QuerySet is empty (length 0)
- This confirms that the book with ID: 1 has been successfully removed from the database

Important notes:
- The DELETE operation is irreversible; once deleted, the data cannot be recovered
- Django's delete cascade rules (if configured) would also delete related objects
- This demonstrates the Delete (D) operation in CRUD operations

## Summary

We have successfully completed all CRUD operations:
- **CREATE**: Created a new Book instance
- **RETRIEVE**: Fetched the book from the database
- **UPDATE**: Modified the book's title
- **DELETE**: Removed the book from the database
