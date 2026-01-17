# RETRIEVE Operation

## Objective
Retrieve and display all attributes of the book that was created in the CREATE operation.

## Python Command

```python
from bookshelf.models import Book

retrieved_book = Book.objects.get(id=1)

# Access and display all attributes
print(f"ID: {retrieved_book.id}")
print(f"Title: {retrieved_book.title}")
print(f"Author: {retrieved_book.author}")
print(f"Publication Year: {retrieved_book.publication_year}")
```

## Output

```
Book retrieved successfully

ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949
```

## Explanation

The `Book.objects.get()` method:
1. Queries the database for a Book with the specified ID
2. Returns the single matching Book instance
3. Raises a `DoesNotExist` exception if no matching book is found

Once retrieved, we can access any field of the Book instance directly using dot notation:
- `retrieved_book.id` - the primary key
- `retrieved_book.title` - the book's title
- `retrieved_book.author` - the book's author
- `retrieved_book.publication_year` - the year of publication

This demonstrates the Read (R) operation in CRUD operations.
