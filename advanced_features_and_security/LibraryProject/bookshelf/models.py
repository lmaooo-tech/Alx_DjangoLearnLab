from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
	"""Custom manager to handle user creation with extra fields."""

	use_in_migrations = True

	def _create_user(self, username, email, password, **extra_fields):
		if not username:
			raise ValueError('The username must be set')
		email = self.normalize_email(email)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(username, email, password, **extra_fields)

	def create_superuser(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(username, email, password, **extra_fields)


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

	class Meta:
		permissions = [
			('can_view', 'Can view books'),
			('can_create', 'Can create books'),
			('can_edit', 'Can edit books'),
			('can_delete', 'Can delete books'),
		]

