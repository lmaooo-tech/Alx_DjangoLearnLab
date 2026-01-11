from django.contrib import admin
from .models import Book


class BookAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the Book model.
    
    Features:
    - Display list_display: Shows title, author, and publication_year in the list view
    - list_filter: Enables filtering by publication_year
    - search_fields: Enables searching by title and author
    """
    
    # Fields to display in the list view
    list_display = ['title', 'author', 'publication_year']
    
    # Fields to filter by in the admin interface
    list_filter = ['publication_year', 'author']
    
    # Fields to search by in the admin interface
    search_fields = ['title', 'author']
    
    # Fields to display when editing a book
    fields = ['title', 'author', 'publication_year']


# Register the Book model with the custom admin configuration
admin.site.register(Book, BookAdmin)

