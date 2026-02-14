import django_filters
from .models import Book, Author


class BookFilter(django_filters.FilterSet):
    """
    Advanced filter class for the Book model.
    Provides multiple filtering options including exact match, case-insensitive, and range filters.
    """
    # Exact match filter for title
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title (contains)')
    
    # Filter by author name (through the related Author model)
    author_name = django_filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains',
        label='Author Name (contains)'
    )
    
    # Exact year filter
    publication_year = django_filters.NumberFilter(label='Publication Year (exact)')
    
    # Range filters for publication year
    publication_year_min = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',
        label='Publication Year (from)'
    )
    publication_year_max = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',
        label='Publication Year (to)'
    )
    
    # Exact author ID filter
    author = django_filters.NumberFilter(field_name='author__id', label='Author ID')
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'author_name', 'publication_year', 'publication_year_min', 'publication_year_max']


class AuthorFilter(django_filters.FilterSet):
    """
    Filter class for the Author model.
    Allows filtering authors by name.
    """
    name = django_filters.CharFilter(lookup_expr='icontains', label='Author Name (contains)')
    
    class Meta:
        model = Author
        fields = ['name']
