from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookshelf.models import CustomUser


class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ('can_view', 'Can view books'),
            ('can_create', 'Can create books'),
            ('can_edit', 'Can edit books'),
            ('can_delete', 'Can delete books'),
        ]


class Library(models.Model):
    name = models.CharField(max_length=200)
    books = models.ManyToManyField(Book)

    def __str__(self):
        return self.name


class Librarian(models.Model):
    name = models.CharField(max_length=200)
    library = models.OneToOneField(Library, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extended user model that includes user roles.
    Linked to Django's built-in User model with a one-to-one relationship.
    """
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Librarian', 'Librarian'),
        ('Member', 'Member'),
    ]
    # Link to the project's configured user model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Member')

    def __str__(self):
        return f'{self.user.username} - {self.role}'


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new user is created.
    """
    if created:
        UserProfile.objects.create(user=instance, role='Member')


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the user's profile whenever the user object is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()