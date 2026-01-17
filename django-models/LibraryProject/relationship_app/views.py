from django.shortcuts import render
from django.views.generic import DetailView
from .models import Book, Library

# Create your views here.

def list_all_books(request):
    """
    Function-based view that lists all books stored in the database.
    Displays book titles and their authors.
    """
    books = Book.objects.all().select_related('author')
    context = {
        'books': books
    }
    return render(request, 'relationship_app/books_list.html', context)


class LibraryDetailView(DetailView):
    """
    Class-based view that displays details for a specific library.
    Shows all books available in that library.
    Uses Django's DetailView generic class.
    """
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        """Add books to the context."""
        context = super().get_context_data(**kwargs)
        library = self.get_object()
        context['books'] = library.books.all().select_related('author')
        return context
