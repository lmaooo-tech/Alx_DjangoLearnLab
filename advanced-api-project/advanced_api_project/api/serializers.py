from rest_framework import serializers
from datetime import datetime
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    BookSerializer - Serializes Book model instances for API responses.
    
    Purpose:
    - Converts Book model instances to JSON representation
    - Handles deserialization of incoming JSON data
    - Provides custom validation logic for book data
    
    Fields Included:
    - id (read-only): The primary key of the book
    - title: The book's title
    - publication_year: The year the book was published
    - author: The ID of the associated author (foreign key)
    
    Custom Validation:
    - validate_publication_year(): Ensures the publication_year is not in the future
      * Raises ValidationError if the year is greater than the current year
      * Prevents invalid future publication dates from being saved
    
    Relationship Handling:
    - The 'author' field is serialized as the author's ID (not nested)
    - This provides a simple reference to the author without embedding full author data
    - Use AuthorSerializer for nested author details if needed
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
    
    def validate_publication_year(self, value):
        """Validate that publication_year is not in the future"""
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    AuthorSerializer - Serializes Author model instances with nested related books.
    
    Purpose:
    - Converts Author model instances to JSON representation
    - Includes nested serialization of all related books
    - Provides a complete author profile with their book catalog
    
    Fields Included:
    - id (read-only): The primary key of the author
    - name: The author's name
    - books (nested): A list of all books written by the author
    
    Relationship Handling:
    - books field: Uses BookSerializer with many=True to serialize all related books
      * The 'books' related_name from Book.author foreign key enables this reverse relationship
      * read_only=True: Books cannot be created/modified through this serializer
      * Provides nested JSON objects for each book, including book details
    
    Data Structure:
    When an Author is serialized, the output looks like:
    {
        "id": 1,
        "name": "Author Name",
        "books": [
            {"id": 1, "title": "Book Title", "publication_year": 2023, "author": 1},
            {"id": 2, "title": "Another Book", "publication_year": 2022, "author": 1}
        ]
    }
    
    Use Cases:
    - Retrieving full author profiles with complete book information
    - Displaying author pages with their complete bibliography
    - API endpoints that need to show author details and all their books
    """
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
