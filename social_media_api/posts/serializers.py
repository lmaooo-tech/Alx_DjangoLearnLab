from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Like, Comment

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying author information in posts and comments.
    """
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'is_following')
        read_only_fields = fields

    def get_is_following(self, obj):
        """Check if the current user is following this author."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying comments on posts.
    """
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'author_id', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'author')

    def create(self, validated_data):
        """Create a comment."""
        validated_data.pop('author_id', None)  # Remove author_id if provided
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying likes on posts.
    """
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')
        read_only_fields = fields


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a post with all related information.
    Includes author details, comments, and likes.
    """
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'author_id', 'content', 'image',
            'likes', 'likes_count', 'is_liked_by_user',
            'comments', 'comments_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'author', 'likes', 'comments')

    def get_likes_count(self, obj):
        """Return the count of likes."""
        return obj.likes.count()

    def get_comments_count(self, obj):
        """Return the count of comments."""
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        """Create a post and set the author to the current user."""
        validated_data.pop('author_id', None)  # Remove author_id if provided
        return super().create(validated_data)


class FeedPostSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying posts in a user's feed.
    This is a lighter version of PostSerializer for feed display.
    """
    author = AuthorSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'content', 'image',
            'likes_count', 'is_liked_by_user',
            'comments_count', 'created_at', 'updated_at'
        )
        read_only_fields = fields

    def get_likes_count(self, obj):
        """Return the count of likes."""
        return obj.likes.count()

    def get_comments_count(self, obj):
        """Return the count of comments."""
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new post.
    Only accepts content and optional image.
    """
    class Meta:
        model = Post
        fields = ('content', 'image')

    def create(self, validated_data):
        """Create a post and set the author to the current user."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
