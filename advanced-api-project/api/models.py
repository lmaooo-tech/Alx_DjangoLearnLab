from django.db import models

# Create your models here.

class Author(models.Model):
    """
    Author model to store author information.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model to store book information.
    Establishes a one-to-many relationship with Author.
    """
    title = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.title
