from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceView

# Create router for NotificationViewSet
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Include router URLs (provides list, retrieve, actions)
    path('', include(router.urls)),
    
    # Notification preferences endpoints
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
]
