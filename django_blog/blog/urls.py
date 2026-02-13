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
    path('posts/new/', views.PostCreateView.as_view(), name='post_create'),
    
    # View single post details
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Edit existing post
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    
    # Delete post
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # ========================================================================
    # Author/User URLs
    # ========================================================================
    # View all posts by a specific user
    path('users/<int:pk>/posts/', views.UserPostsView.as_view(), name='user_posts'),
]

