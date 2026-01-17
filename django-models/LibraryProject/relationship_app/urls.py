from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import list_all_books, register_view, login_view, logout_view
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view: List all books
    path('books/', list_all_books, name='list_books'),
    
    # Class-based view: Library detail with books
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
    
    # Authentication views
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
]
