from django.contrib import admin
from .models import UserProfile, Post, Comment


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'location', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'get_tags')
    list_filter = ('published_date', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('published_date',)
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'content', 'author')
        }),
        ('Tags', {
            'fields': ('tags',)
        }),
        ('Metadata', {
            'fields': ('published_date',),
            'classes': ('collapse',)
        }),
    )

    def get_tags(self, obj):
        """Display tags in admin list view"""
        return ', '.join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'post')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Comment Content', {
            'fields': ('post', 'author', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
