# UPDATE Operation

## Objective
Update the title of the book "1984" to "Nineteen Eighty-Four" and save the changes to the database.

## Python Command

```python
from bookshelf.models import Book

# Retrieve the book
retrieved_book = Book.objects.get(id=1)

# Update the title field
retrieved_book.title = 'Nineteen Eighty-Four'

# Save the changes to the database
retrieved_book.save()
```

## Output

```
Book updated successfully
New Title: Nineteen Eighty-Four

Verification - Title in database: Nineteen Eighty-Four
```

## Explanation

The UPDATE operation in Django involves three steps:

1. **Retrieve the instance**: Use `Book.objects.get()` to fetch the book from the database
2. **Modify the field**: Change the desired attribute (in this case, `title`)
3. **Save the changes**: Call the `.save()` method to persist the changes back to the database

The `.save()` method:
- Detects which fields have changed
- Executes an UPDATE SQL query with only the changed fields
- Updates the instance in the database

After the save operation, the book in the database now has:
- ID: 1
- Title: "Nineteen Eighty-Four" (updated)
- Author: "George Orwell" (unchanged)
- Publication Year: 1949 (unchanged)

This demonstrates the Update (U) operation in CRUD operations.
