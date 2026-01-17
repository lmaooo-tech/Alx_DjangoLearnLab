from django.urls import path
from .views import list_books
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view: List all books
    path('books/', list_books, name='list_books'),
    
    # Class-based view: Library detail with books
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
]
