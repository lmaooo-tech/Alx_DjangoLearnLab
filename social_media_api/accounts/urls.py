from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Follow/Unfollow endpoints - Primary paths
    path('follow/<int:user_id>/', views.follow_user_view, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user_view, name='unfollow-user'),
    
    # Follow/Unfollow endpoints - Alternative paths for non-router access
    path('users/<int:user_id>/follow/', views.follow_user_view, name='follow-user-alt'),
    path('users/<int:user_id>/unfollow/', views.unfollow_user_view, name='unfollow-user-alt'),
    
    # Router URLs (includes follow/unfollow from UserViewSet actions)
    path('', include(router.urls)),
]

