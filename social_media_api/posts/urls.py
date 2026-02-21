from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'posts'

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')

urlpatterns = [
    # Feed endpoints
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('feed/<str:username>/', views.UserFeedView.as_view(), name='user-feed'),
    
    # Alternative feed endpoint using function-based view
    path('feed-alt/', views.feed_view, name='feed-alt'),
    
    # Explore endpoint for discovering posts
    path('explore/', views.explore_view, name='explore'),
    
    # Like and Unlike endpoints
    path('posts/<int:pk>/like/', views.PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('posts/<int:pk>/unlike/', views.PostViewSet.as_view({'post': 'unlike'}), name='post-unlike'),
    
    # Router URLs (includes post CRUD operations and custom actions)
    path('', include(router.urls)),
]
