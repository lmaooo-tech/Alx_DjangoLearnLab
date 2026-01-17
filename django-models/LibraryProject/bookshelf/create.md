# CREATE Operation

## Objective
Create a Book instance with the following details:
- Title: "1984"
- Author: "George Orwell"
- Publication Year: 1949

## Python Command

```python
from bookshelf.models import Book

book = Book.objects.create(
    title='1984',
    author='George Orwell',
    publication_year=1949
)
```

## Output

```
Book created with ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949
```

## Explanation

The `Book.objects.create()` method is a Django ORM shortcut that:
1. Creates a new Book instance with the provided field values
2. Automatically saves the instance to the database in a single operation
3. Returns the created instance with its generated primary key (ID: 1)

The book is now permanently stored in the database and can be retrieved, updated, or deleted using its ID.
