from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from .models import Library

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
    return render(request, 'relationship_app/list_books.html', context)


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


# Authentication Views

def register_view(request):
    """
    User registration view.
    Handles user account creation with username, email, and password.
    Uses Django's UserCreationForm for form validation.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('relationship_app:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('relationship_app:register')
    else:
        form = UserCreationForm()

    context = {
        'form': form
    }
    return render(request, 'relationship_app/register.html', context)


def login_view(request):
    """
    User login view.
    Authenticates user credentials and creates a session.
    """
    if request.user.is_authenticated:
        return redirect('relationship_app:list_books')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('relationship_app:list_books')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('relationship_app:login')

    return render(request, 'relationship_app/login.html')


def logout_view(request):
    """
    User logout view.
    Clears the user session and redirects to home page.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('relationship_app:list_books')
