from django.urls import path
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view: List all books
    path('books/', views.list_all_books, name='list_books'),
    
    # Class-based view: Library detail with books
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
]
