from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # ========================================================================
    # Authentication URLs
    # ========================================================================
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # ========================================================================
    # Blog Post CRUD URLs
    # ========================================================================
    # List all posts
    path('', views.PostListView.as_view(), name='post_list'),
    path('posts/', views.PostListView.as_view(), name='posts'),
    
    # Create new post
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    
    # View single post details
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Update existing post
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_edit'),
    
    # Delete post
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # ========================================================================
    # Comment CRUD URLs
    # ========================================================================
    # Create new comment on a post
    path('post/<int:pk>/comments/new/', views.CommentCreateView.as_view(), name='comment_create'),
    
    # Update existing comment
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_edit'),
    
    # Delete comment
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # ========================================================================
    # Author/User URLs
    # ========================================================================
    # View all posts by a specific user
    path('users/<int:pk>/posts/', views.UserPostsView.as_view(), name='user_posts'),
    
    # ========================================================================
    # Search and Tag URLs
    # ========================================================================
    # Advanced search with filters
    path('search/', views.PostSearchView.as_view(), name='search'),
    
    # View all posts with a specific tag
    path('tags/<slug:slug>/', views.TagArchiveView.as_view(), name='tag_archive'),
]

