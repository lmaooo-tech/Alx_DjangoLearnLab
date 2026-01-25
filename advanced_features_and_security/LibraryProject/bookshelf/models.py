from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
	"""Custom manager to handle user creation with extra fields."""

	def create_user(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		user = super().create_user(username=username, email=email, password=password, **extra_fields)
		return user

	def create_superuser(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		user = super().create_superuser(username=username, email=email, password=password, **extra_fields)
		return user


class CustomUser(AbstractUser):
	"""Custom user model with date_of_birth and profile_photo."""
	date_of_birth = models.DateField(null=True, blank=True)
	profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

	objects = CustomUserManager()

	def __str__(self):
		return self.username


class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	publication_year = models.IntegerField()

	def __str__(self):
		return self.title

