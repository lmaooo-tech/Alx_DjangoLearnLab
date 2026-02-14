from django.db import models


class Author(models.Model):
    """
    Author Model - Represents the author of books in the system.
    
    Purpose:
    - Stores information about book authors
    - Serves as the parent model in a one-to-many relationship with Book
    - Allows multiple books to be associated with a single author
    
    Fields:
    - name (CharField): The author's name, stored as a string with a maximum length of 200 characters
    
    Relationships:
    - Books (reverse relation): Through the 'books' related_name, this model can access all books
      written by an author using author.books.all()
    
    Usage:
    - Create author instances to represent individual authors
    - Access related books through the reverse relationship (author.books)
    """
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book Model - Represents a book in the library system.
    
    Purpose:
    - Stores book information including title and publication year
    - Implements a many-to-one relationship with the Author model
    - Each book belongs to exactly one author, but an author can have multiple books
    
    Fields:
    - title (CharField): The book's title, stored as a string with a maximum length of 200 characters
    - publication_year (IntegerField): The year the book was published
    - author (ForeignKey): A foreign key linking to the Author model
        * on_delete=models.CASCADE: If an author is deleted, all their books are also deleted
        * related_name='books': Allows reverse access from Author to Book using author.books.all()
    
    Relationships:
    - Author (forward relation): Each book has exactly one author via the 'author' field
    - Reverse access from Author: Authors can access their books using the 'books' related name
    
    Usage:
    - Create book instances with a reference to an author
    - Query books by author using book.author
    - Access all books by an author using author.books.all()
    """
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    
    def __str__(self):
        return self.title
