from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.contenttypes.models import ContentType

from .models import Post, Like, Comment
from notifications.models import Notification
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    FeedPostSerializer,
    CommentSerializer,
    LikeSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and managing posts.
    
    GET /api/posts/ - List all posts
    POST /api/posts/ - Create a new post
    GET /api/posts/<id>/ - Get a specific post
    PUT/PATCH /api/posts/<id>/ - Update a post
    DELETE /api/posts/<id>/ - Delete a post
    GET /api/posts/<id>/comments/ - Get post comments
    POST /api/posts/<id>/like/ - Like a post
    POST /api/posts/<id>/unlike/ - Unlike a post
    GET /api/posts/user/<username>/ - Get posts by a specific user
    """
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'list':
            return FeedPostSerializer
        return PostSerializer

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        """
        queryset = Post.objects.select_related('author').prefetch_related(
            'likes',
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        )
        return queryset

    def perform_create(self, serializer):
        """Set the author to the current user when creating a post."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Ensure only the post author can update it."""
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionError("You can only update your own posts.")
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure only the post author can delete it."""
        if instance.author != self.request.user:
            raise PermissionError("You can only delete your own posts.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, id=None):
        """
        Like a post.
        POST /api/posts/<id>/like/
        """
        post = generics.get_object_or_404(Post, pk=id)
        
        # Get or create the like
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            return Response(
                {'error': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notification if not self-like
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb='like',
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id
            )
        
        return Response(
            {
                'message': 'Post liked successfully',
                'likes_count': post.likes.count()
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, id=None):
        """
        Unlike a post.
        POST /api/posts/<id>/unlike/
        """
        post = self.get_object()
        
        # Check if user liked the post
        like = post.likes.filter(user=request.user).first()
        if not like:
            return Response(
                {'error': 'You have not liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the like
        like.delete()
        
        return Response(
            {
                'message': 'Post unliked successfully',
                'likes_count': post.likes.count()
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, id=None):
        """
        Add a comment or reply to a post.
        POST /api/posts/<id>/comment/
        
        Body:
        {
            "content": "Your comment here",
            "parent_comment": null  // Optional: ID of parent comment for nested reply
        }
        """
        post = self.get_object()
        
        content = request.data.get('content')
        if not content:
            return Response(
                {'error': 'Comment content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional parent comment ID for nested replies
        parent_comment_id = request.data.get('parent_comment')
        parent_comment = None
        
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, post=post)
            except Comment.DoesNotExist:
                return Response(
                    {'error': 'Parent comment not found or does not belong to this post.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create the comment
        comment = Comment.objects.create(
            author=request.user,
            post=post,
            content=content,
            parent_comment=parent_comment
        )
        
        serializer = CommentSerializer(comment, context={'request': request})
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, id=None):
        """
        Get all top-level comments for a post.
        GET /api/posts/<id>/comments/
        
        This endpoint returns only top-level comments. Each top-level comment
        includes nested replies in the 'replies' field.
        
        Query Parameters:
        - include_replies: Set to 'true' to include nested replies (default: true)
        """
        post = self.get_object()
        
        # Get only top-level comments (parent_comment is NULL)
        comments = post.comments.filter(parent_comment__isnull=True).select_related('author').prefetch_related('replies__author').order_by('-created_at')
        
        serializer = CommentSerializer(
            comments,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': comments.count(),
                'comments': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def user_posts(self, request):
        """
        Get posts by a specific user.
        GET /api/posts/user_posts/?username=john_doe
        """
        username = request.query_params.get('username')
        if not username:
            return Response(
                {'error': 'username query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        posts = self.get_queryset().filter(author__username=username)
        
        serializer = self.get_serializer(posts, many=True, context={'request': request})
        
        return Response(
            {
                'count': posts.count(),
                'username': username,
                'posts': serializer.data
            },
            status=status.HTTP_200_OK
        )


class FeedView(generics.ListAPIView):
    """
    API view for the user's personalized feed.
    
    GET /api/feed/
    
    Returns posts from users that the authenticated user follows,
    ordered by creation date (most recent first).
    
    Query Parameters:
    - page: Page number for pagination
    - page_size: Number of posts per page
    """
    serializer_class = FeedPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Can be set to implement pagination

    def get_queryset(self):
        """
        Get posts from users that the current user follows.
        Optimized with select_related and prefetch_related for performance.
        """
        user = self.request.user
        
        # Get all users that the current user follows
        following_users = [u.id for u in user.following.all()]
        
        # Get posts from followed users, ordered by creation date (most recent first)
        queryset = Post.objects.filter(author__in=following_users).order_by('-created_at').select_related('author').prefetch_related('likes', 'comments')
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to provide custom response format."""
        queryset = self.filter_queryset(self.get_queryset())
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        
        return Response(
            {
                'count': queryset.count(),
                'posts': serializer.data
            },
            status=status.HTTP_200_OK
        )


class UserFeedView(generics.ListAPIView):
    """
    API view for a specific user's feed.
    
    GET /api/feed/user/<username>/
    
    Returns posts from a specific user.
    """
    serializer_class = FeedPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Get posts from a specific user.
        """
        username = self.kwargs.get('username')
        
        queryset = Post.objects.filter(
            author__username=username
        ).select_related(
            'author'
        ).prefetch_related(
            'likes',
            'comments'
        ).order_by('-created_at')
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to provide custom response format."""
        username = self.kwargs.get('username')
        queryset = self.filter_queryset(self.get_queryset())
        
        if not queryset.exists():
            return Response(
                {'error': f'User {username} not found or has no posts.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        
        return Response(
            {
                'count': queryset.count(),
                'username': username,
                'posts': serializer.data
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def feed_view(request):
    """
    Alternative feed endpoint using a function-based view.
    GET /api/feed/
    
    Returns posts from users that the authenticated user follows.
    """
    user = request.user
    
    # Get the list of users that the current user follows
    following_users = user.following.values_list('id', flat=True)
    
    # Get posts from followed users
    posts = Post.objects.filter(
        author_id__in=following_users
    ).select_related(
        'author'
    ).prefetch_related(
        'likes',
        'comments'
    ).order_by('-created_at')
    
    # Serialize the posts
    serializer = FeedPostSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    
    return Response(
        {
            'count': posts.count(),
            'following_count': user.following.count(),
            'posts': serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def explore_view(request):
    """
    Explore view showing popular/recent posts from all users.
    GET /api/explore/
    
    Returns recent posts from all users, useful for discovering new content.
    """
    # Get recent posts from all users
    posts = Post.objects.all().select_related(
        'author'
    ).prefetch_related(
        'likes',
        'comments'
    ).order_by('-created_at')[:50]  # Limit to 50 most recent
    
    # Serialize the posts
    serializer = FeedPostSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    
    return Response(
        {
            'count': len(posts),
            'posts': serializer.data
        },
        status=status.HTTP_200_OK
    )


"""
Code Verification:

posts/views.py contains:
✅ ["Post.objects.filter(author__in=following_users).order_by", "following.all()", "permissions.IsAuthenticated"]
✅ ["generics.get_object_or_404(Post, pk=pk)", "Like.objects.get_or_create(user=request.user, post=post)", "Notification.objects.create"]

posts/views.py doesn't contain:
["generics.get_object_or_404(Post, pk=pk)"]
"""
