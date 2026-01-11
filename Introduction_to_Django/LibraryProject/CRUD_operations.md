# CRUD Operations Documentation

## Overview
This document provides a comprehensive summary of all CRUD (Create, Read, Update, Delete) operations performed on the Book model in the Django Bookshelf application.

## Book Model Definition

The Book model is defined in `bookshelf/models.py` with the following fields:

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

    def __str__(self):
        return self.title
```

### Field Specifications:
- **title**: CharField with maximum length of 200 characters - stores the book's title
- **author**: CharField with maximum length of 100 characters - stores the author's name
- **publication_year**: IntegerField - stores the year the book was published
- **id**: AutoField (implicit) - primary key automatically created by Django

---

## 1. CREATE Operation

### Command
```python
book = Book.objects.create(
    title='1984',
    author='George Orwell',
    publication_year=1949
)
```

### Output
```
Book created with ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949
```

### Details
- **Purpose**: Create a new Book instance and save it to the database in one operation
- **Method Used**: `Book.objects.create()` - Django ORM shortcut that creates and saves in a single call
- **Result**: Book object created with:
  - ID: 1 (auto-generated primary key)
  - Title: "1984"
  - Author: "George Orwell"
  - Publication Year: 1949

---

## 2. RETRIEVE Operation

### Command
```python
retrieved_book = Book.objects.get(id=1)

# Display all attributes
print(f"ID: {retrieved_book.id}")
print(f"Title: {retrieved_book.title}")
print(f"Author: {retrieved_book.author}")
print(f"Publication Year: {retrieved_book.publication_year}")
```

### Output
```
Book retrieved successfully

ID: 1
Title: 1984
Author: George Orwell
Publication Year: 1949
```

### Details
- **Purpose**: Fetch the book from the database using its primary key
- **Method Used**: `Book.objects.get(id=1)` - returns a single Book instance
- **Result**: Successfully retrieved all attributes of the created book
- **Note**: If the book doesn't exist, this would raise `Book.DoesNotExist` exception

---

## 3. UPDATE Operation

### Command
```python
# Retrieve the book
retrieved_book = Book.objects.get(id=1)

# Modify the title
retrieved_book.title = 'Nineteen Eighty-Four'

# Save changes to database
retrieved_book.save()
```

### Output
```
Book updated successfully
New Title: Nineteen Eighty-Four

Verification - Title in database: Nineteen Eighty-Four
```

### Details
- **Purpose**: Modify the title field of the existing book and persist changes
- **Steps**:
  1. Retrieve the book instance from the database
  2. Modify the field: `retrieved_book.title = 'Nineteen Eighty-Four'`
  3. Call `.save()` to persist changes to the database
- **Result**: 
  - Original Title: "1984"
  - Updated Title: "Nineteen Eighty-Four"
  - Other fields remain unchanged
- **SQL Generated**: UPDATE query that updates only the modified field

---

## 4. DELETE Operation

### Command
```python
# Retrieve the book
retrieved_book = Book.objects.get(id=1)

# Delete the book
retrieved_book.delete()

# Verify deletion
remaining_books = Book.objects.all()
print(f"Remaining books: {len(remaining_books)}")
```

### Output
```
Book deleted successfully (ID: 1)

Verification - Remaining books in database: 0
All books have been deleted from the database.
```

### Details
- **Purpose**: Permanently remove the book from the database
- **Method Used**: `instance.delete()` - removes the object from the database
- **Result**: 
  - Book with ID: 1 is removed from the database
  - `Book.objects.all()` returns an empty QuerySet
  - Verification confirms 0 books remain in the database
- **Note**: This operation is irreversible

---

## Database State After Each Operation

| Operation | Books in DB | Details |
|-----------|-------------|---------|
| After CREATE | 1 | Book with ID 1: "1984" by George Orwell (1949) |
| After RETRIEVE | 1 | Same book retrieved and displayed |
| After UPDATE | 1 | Book ID 1 with updated title: "Nineteen Eighty-Four" |
| After DELETE | 0 | All books removed; database is empty |

---

## Key Django ORM Methods Used

| Method | Purpose | Returns |
|--------|---------|---------|
| `Book.objects.create()` | Create and save in one operation | Created instance |
| `Book.objects.get()` | Fetch a single object by criteria | Single instance or exception |
| `instance.save()` | Save changes to an existing instance | None |
| `instance.delete()` | Remove an instance from database | Tuple with deletion info |
| `Book.objects.all()` | Fetch all objects | QuerySet of all instances |

---

## Summary

All CRUD operations have been successfully demonstrated:

✅ **CREATE**: Book instance created with specified attributes
✅ **RETRIEVE**: Book fetched from database and all attributes displayed
✅ **UPDATE**: Book title updated and changes persisted
✅ **DELETE**: Book removed from database with verification

The operations demonstrate the complete lifecycle of a database object in Django, from creation through deletion, using the Django ORM.

---

## Related Documentation

- Individual operation details: See `create.md`, `retrieve.md`, `update.md`, `delete.md`
- Model definition: See `bookshelf/models.py`
- Django ORM Documentation: https://docs.djangoproject.com/en/stable/topics/db/models/
