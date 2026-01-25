import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from bookshelf.models import Book

print("=" * 60)
print("CRUD OPERATIONS DEMO")
print("=" * 60)

# CREATE
print("\n1. CREATE OPERATION")
print("-" * 60)
print("Command: book = Book.objects.create(title='1984', author='George Orwell', publication_year=1949)")
book = Book.objects.create(title='1984', author='George Orwell', publication_year=1949)
print(f"Output: Book created with ID: {book.id}")
print(f"        Title: {book.title}, Author: {book.author}, Year: {book.publication_year}")

# RETRIEVE
print("\n2. RETRIEVE OPERATION")
print("-" * 60)
print("Command: retrieved_book = Book.objects.get(id=1)")
retrieved_book = Book.objects.get(id=book.id)
print(f"Output: Book retrieved successfully")
print(f"        ID: {retrieved_book.id}")
print(f"        Title: {retrieved_book.title}")
print(f"        Author: {retrieved_book.author}")
print(f"        Publication Year: {retrieved_book.publication_year}")

# UPDATE
print("\n3. UPDATE OPERATION")
print("-" * 60)
print("Command: retrieved_book.title = 'Nineteen Eighty-Four'")
print("         retrieved_book.save()")
retrieved_book.title = 'Nineteen Eighty-Four'
retrieved_book.save()
print(f"Output: Book updated successfully")
print(f"        New Title: {retrieved_book.title}")

# Verify update
updated_book = Book.objects.get(id=book.id)
print(f"        Verification - Title in database: {updated_book.title}")

# DELETE
print("\n4. DELETE OPERATION")
print("-" * 60)
print("Command: retrieved_book.delete()")
deleted_book_id = retrieved_book.id
retrieved_book.delete()
print(f"Output: Book deleted successfully (ID: {deleted_book_id})")

# Verify deletion
remaining_books = Book.objects.all()
print(f"        Verification - Remaining books in database: {len(remaining_books)}")
if len(remaining_books) == 0:
    print(f"        All books have been deleted from the database.")

print("\n" + "=" * 60)
print("CRUD OPERATIONS COMPLETED")
print("=" * 60)
