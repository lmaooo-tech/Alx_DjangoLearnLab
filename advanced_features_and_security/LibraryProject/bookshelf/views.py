from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from .models import Book
from .forms import BookSearchForm
from .forms import ExampleForm


@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
	"""Display all books; requires the can_view permission."""
	form = BookSearchForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		query = form.cleaned_data.get('query')
		books = Book.objects.filter(title__icontains=query) if query else Book.objects.all()
	else:
		books = Book.objects.all()
	context = {'books': books, 'form': form}
	return render(request, 'bookshelf/book_list.html', context)
