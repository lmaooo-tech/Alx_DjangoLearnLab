"""
Sample queries for relationship_app models
Demonstrates ForeignKey, ManyToManyField, and OneToOneField relationships
"""

from .models import Author, Book, Library, Librarian

# Query 1: Get all books by a specific author
# Using ForeignKey relationship
def get_books_by_author(author_id):
    """
    Query all books written by a specific author.
    Uses ForeignKey relationship from Book to Author.
    """
    author = Author.objects.get(id=author_id)
    books = Book.objects.filter(author=author)
    # Alternative: books = author.book_set.all()
    return books


# Query 2: List all books in a library
# Using ManyToManyField relationship
def get_books_in_library(library_id):
    """
    Query all books available in a specific library.
    Uses ManyToManyField relationship between Library and Book.
    """
    library = Library.objects.get(id=library_id)
    books = library.books.all()
    return books


# Query 3: Retrieve the librarian for a library
# Using OneToOneField relationship
def get_librarian_for_library(library_id):
    """
    Query the librarian responsible for a specific library.
    Uses OneToOneField relationship between Librarian and Library.
    """
    library = Library.objects.get(id=library_id)
    librarian = Librarian.objects.get(library=library)
    # Alternative: librarian = library.librarian
    return librarian


# Additional helpful queries

def get_all_authors():
    """Get all authors in the database."""
    return Author.objects.all()


def get_all_books():
    """Get all books in the database."""
    return Book.objects.all()


def get_all_libraries():
    """Get all libraries in the database."""
    return Library.objects.all()


def get_all_librarians():
    """Get all librarians in the database."""
    return Librarian.objects.all()


# Example usage (uncomment to use in Django shell)
"""
# In Django shell: python manage.py shell

# Create sample data
author1 = Author.objects.create(name="J.K. Rowling")
book1 = Book.objects.create(title="Harry Potter and the Philosopher's Stone", author=author1)
book2 = Book.objects.create(title="Harry Potter and the Chamber of Secrets", author=author1)

library1 = Library.objects.create(name="Central Library")
library1.books.add(book1, book2)

librarian1 = Librarian.objects.create(name="John Doe", library=library1)

# Test queries
books = get_books_by_author(author1.id)
print(f"Books by {author1.name}: {[book.title for book in books]}")

library_books = get_books_in_library(library1.id)
print(f"Books in {library1.name}: {[book.title for book in library_books]}")

librarian = get_librarian_for_library(library1.id)
print(f"Librarian for {library1.name}: {librarian.name}")
"""
