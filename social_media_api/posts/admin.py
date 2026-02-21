from django.contrib import admin
from .models import Post, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface for Post model.
    """
    list_display = ('id', 'author', 'content_preview', 'created_at', 'likes_count')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'content')
    readonly_fields = ('created_at', 'updated_at', 'id')
    ordering = ('-created_at',)

    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'content', 'image')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        """Display a preview of the post content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def likes_count(self, obj):
        """Display the count of likes."""
        return obj.likes.count()
    likes_count.short_description = 'Likes'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin interface for Like model.
    """
    list_display = ('id', 'user', 'post_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'post__author__username')
    readonly_fields = ('created_at', 'id')
    ordering = ('-created_at',)

    def post_preview(self, obj):
        """Display a preview of the post being liked."""
        preview = obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
        return f'Post by {obj.post.author.username}: {preview}'
    post_preview.short_description = 'Post'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    """
    list_display = ('id', 'author', 'post_preview', 'content_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'post__author__username', 'content')
    readonly_fields = ('created_at', 'updated_at', 'id')
    ordering = ('-created_at',)

    fieldsets = (
        ('Comment Information', {
            'fields': ('author', 'post', 'content')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def post_preview(self, obj):
        """Display a preview of the post being commented on."""
        preview = obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
        return f'Post by {obj.post.author.username}: {preview}'
    post_preview.short_description = 'Post'

    def content_preview(self, obj):
        """Display a preview of the comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'
