from django.urls import path
from .views import book_list

app_name = 'bookshelf'

urlpatterns = [
    path('books/', book_list, name='book_list'),
]
