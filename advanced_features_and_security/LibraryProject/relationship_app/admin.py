from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from bookshelf.models import CustomUser
from .models import Author, Book, Library, Librarian, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	list_display = (
		'username', 'email', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active'
	)
	list_filter = ('is_staff', 'is_superuser', 'is_active')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	ordering = ('username',)

	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'profile_photo')}),
		('Permissions', {'fields': (
			'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
		)}),
		('Important dates', {'fields': ('last_login', 'date_joined')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'password1', 'password2', 'email', 'date_of_birth', 'profile_photo'),
		}),
	)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')
	list_filter = ('role',)
	search_fields = ('user__username',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author')
	search_fields = ('title',)


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
	list_display = ('name', 'library')
