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
    
    # Router URLs
    path('', include(router.urls)),
]
