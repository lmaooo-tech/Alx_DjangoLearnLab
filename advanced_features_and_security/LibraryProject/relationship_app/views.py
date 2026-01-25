from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Book, Library, UserProfile, Author

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


def register(request):
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

# Role-Based Access Control Functions

def is_admin(user):
    """
    Check if the user has the 'Admin' role.
    """
    if user.is_authenticated:
        try:
            return user.profile.role == 'Admin'
        except UserProfile.DoesNotExist:
            return False
    return False


def is_librarian(user):
    """
    Check if the user has the 'Librarian' role.
    """
    if user.is_authenticated:
        try:
            return user.profile.role == 'Librarian'
        except UserProfile.DoesNotExist:
            return False
    return False


def is_member(user):
    """
    Check if the user has the 'Member' role.
    """
    if user.is_authenticated:
        try:
            return user.profile.role == 'Member'
        except UserProfile.DoesNotExist:
            return False
    return False


@login_required
@user_passes_test(is_admin)
def admin_view(request):
    """
    Admin-only view for administrative tasks.
    Only users with the 'Admin' role can access this view.
    """
    context = {
        'user': request.user,
        'role': request.user.profile.role,
    }
    return render(request, 'relationship_app/admin_view.html', context)


@login_required
@user_passes_test(is_librarian)
def librarian_view(request):
    """
    Librarian-only view for library management tasks.
    Only users with the 'Librarian' role can access this view.
    """
    libraries = Library.objects.all()
    context = {
        'user': request.user,
        'role': request.user.profile.role,
        'libraries': libraries,
    }
    return render(request, 'relationship_app/librarian_view.html', context)


@login_required
@user_passes_test(is_member)
def member_view(request):
    """
    Member-only view for regular members.
    Only users with the 'Member' role can access this view.
    """
    books = Book.objects.all().select_related('author')
    context = {
        'user': request.user,
        'role': request.user.profile.role,
        'books': books,
    }
    return render(request, 'relationship_app/member_view.html', context)


# Book Management Views with Permission Checks

@login_required
@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    """
    View to add a new book to the database.
    Only users with the 'can_add_book' permission can access this view.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')

        if not title or not author_id:
            messages.error(request, 'Please provide both title and author.')
            return redirect('relationship_app:add_book')

        try:
            author = Author.objects.get(id=author_id)
            book = Book.objects.create(title=title, author=author)
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('relationship_app:list_books')
        except Author.DoesNotExist:
            messages.error(request, 'Selected author does not exist.')
            return redirect('relationship_app:add_book')
    else:
        authors = Author.objects.all()
        context = {
            'authors': authors,
        }
        return render(request, 'relationship_app/add_book_form.html', context)


@login_required
@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, pk):
    """
    View to edit an existing book.
    Only users with the 'can_change_book' permission can access this view.
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')

        if not title or not author_id:
            messages.error(request, 'Please provide both title and author.')
            return redirect('relationship_app:edit_book', pk=pk)

        try:
            author = Author.objects.get(id=author_id)
            book.title = title
            book.author = author
            book.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('relationship_app:list_books')
        except Author.DoesNotExist:
            messages.error(request, 'Selected author does not exist.')
            return redirect('relationship_app:edit_book', pk=pk)
    else:
        authors = Author.objects.all()
        context = {
            'book': book,
            'authors': authors,
        }
        return render(request, 'relationship_app/edit_book_form.html', context)


@login_required
@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, pk):
    """
    View to delete a book from the database.
    Only users with the 'can_delete_book' permission can access this view.
    """
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('relationship_app:list_books')
    else:
        context = {
            'book': book,
        }
        return render(request, 'relationship_app/delete_book_confirm.html', context)