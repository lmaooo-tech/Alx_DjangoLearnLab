from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Comment
from .serializers import PostSerializer, PostDetailSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post model.
    Provides CRUD operations for posts.
    
    Features:
    - List all posts (paginated)
    - Filter by author
    - Search by title or content
    - Order by created_at or updated_at
    
    Endpoints:
    - GET /api/posts/ - List all posts
    - POST /api/posts/ - Create a new post (authenticated users)
    - GET /api/posts/{id}/ - Get post details
    - PUT/PATCH /api/posts/{id}/ - Update post (author only)
    - DELETE /api/posts/{id}/ - Delete post (author only)
    - GET /api/posts/{id}/comments/ - Get comments for a post
    
    Query Parameters:
    - page: Page number (default: 1)
    - author: Filter by author ID
    - search: Search in title and content
    - ordering: Order by field (created_at, updated_at, -created_at, -updated_at)
    """
    queryset = Post.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def get_permissions(self):
        """
        Override permissions based on action.
        Allow any user to list and retrieve posts,
        but only authenticated users to create/edit/delete.
        """
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        """Automatically set the author to the current user."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def comments(self, request, pk=None):
        """Get all comments for a specific post."""
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model.
    Provides CRUD operations for comments.
    
    Features:
    - List all comments (paginated)
    - Filter by author or post
    - Search by content
    - Order by created_at or updated_at
    
    Endpoints:
    - GET /api/comments/ - List all comments
    - POST /api/comments/ - Create a new comment (authenticated users)
    - GET /api/comments/{id}/ - Get comment details
    - PUT/PATCH /api/comments/{id}/ - Update comment (author only)
    - DELETE /api/comments/{id}/ - Delete comment (author only)
    
    Query Parameters:
    - page: Page number (default: 1)
    - author: Filter by author ID
    - post: Filter by post ID
    - search: Search in content
    - ordering: Order by field (created_at, updated_at, -created_at, -updated_at)
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['author', 'post']
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Override permissions based on action.
        Allow any user to list and retrieve comments,
        but only authenticated users to create/edit/delete.
        """
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        
        return super().get_permissions()

    def perform_create(self, serializer):
        """Automatically set the author to the current user."""
        serializer.save(author=self.request.user)

