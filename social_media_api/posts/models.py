from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Post(models.Model):
    """
    Post model representing a social media post.
    
    Fields:
        author: Foreign key to the user who created the post
        content: The text content of the post
        image: Optional image attached to the post
        created_at: Timestamp when the post was created
        updated_at: Timestamp when the post was last updated
        likes_count: Denormalized count of likes (for performance)
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="The user who created this post"
    )
    content = models.TextField(
        help_text="The content of the post",
        max_length=5000
    )
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        help_text="optional image for the post"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the post was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the post was last updated"
    )

    class Meta:
        ordering = ['-created_at']  # Most recent first
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"Post by {self.author.username} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_author_info(self):
        """Return author information."""
        return {
            'id': self.author.id,
            'username': self.author.username,
            'email': self.author.email,
            'first_name': self.author.first_name,
            'last_name': self.author.last_name,
            'bio': self.author.bio,
            'profile_picture': self.author.profile_picture.url if self.author.profile_picture else None,
        }


class Like(models.Model):
    """
    Like model representing a user's like on a post.
    
    Fields:
        user: The user who liked the post
        post: The post that was liked
        created_at: Timestamp when the like was created
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="The user who liked the post"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="The post that was liked"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the like was created"
    )

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked post by {self.post.author.username}"


class Comment(models.Model):
    """
    Comment model representing a comment on a post.
    
    Fields:
        author: The user who created the comment
        post: The post being commented on
        content: The text content of the comment
        created_at: Timestamp when the comment was created
        updated_at: Timestamp when the comment was last updated
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The user who created the comment"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The post being commented on"
    )
    content = models.TextField(
        help_text="The content of the comment",
        max_length=1000
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the comment was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on post by {self.post.author.username}"
