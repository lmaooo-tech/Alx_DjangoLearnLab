from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationDetailSerializer,
    NotificationPreferenceSerializer,
    NotificationListSerializer,
    BulkNotificationActionSerializer,
)


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving and managing user notifications.
    
    GET /api/notifications/ - List user's notifications
    GET /api/notifications/<id>/ - Get specific notification
    POST /api/notifications/mark_read/ - Mark notification as read
    POST /api/notifications/mark_all_read/ - Mark all notifications as read
    POST /api/notifications/bulk_action/ - Perform bulk action
    GET /api/notifications/unread_count/ - Get unread notification count
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get notifications for the current user."""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor', 'content_type').order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return NotificationDetailSerializer
        elif self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List user's notifications with optional filtering.
        
        Query parameters:
        - unread: Filter by read status (true/false)
        - verb: Filter by notification type
        """
        queryset = self.get_queryset()
        
        # Filter by read status if specified
        unread = request.query_params.get('unread')
        if unread is not None:
            unread = unread.lower() == 'true'
            queryset = queryset.filter(is_read=False if unread else True)
        
        # Filter by notification type if specified
        verb = request.query_params.get('verb')
        if verb:
            queryset = queryset.filter(verb=verb)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, id=None):
        """
        Mark a specific notification as read.
        POST /api/notifications/<id>/mark_read/
        """
        notification = self.get_object()
        
        # Verify the user owns this notification
        if notification.recipient != request.user:
            return Response(
                {'error': 'You do not have permission to update this notification.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.is_read = True
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(
            {
                'message': 'Notification marked as read',
                'notification': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_read(self, request):
        """
        Mark all user's unread notifications as read.
        POST /api/notifications/mark_all_read/
        """
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response(
            {
                'message': f'Marked {unread_count} notification(s) as read',
                'count': unread_count
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """
        Get count of unread notifications.
        GET /api/notifications/unread_count/
        """
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response(
            {
                'unread_count': count
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bulk_action(self, request):
        """
        Perform bulk action on multiple notifications.
        POST /api/notifications/bulk_action/
        
        Body:
        {
            "notification_ids": [1, 2, 3],
            "action": "mark_read" | "mark_unread" | "delete"
        }
        """
        serializer = BulkNotificationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        action = serializer.validated_data['action']
        
        # Get notifications belonging to current user
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        )
        
        if not notifications.exists():
            return Response(
                {'error': 'No matching notifications found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if action == 'mark_read':
            count = notifications.update(is_read=True)
            message = f'Marked {count} notification(s) as read'
        elif action == 'mark_unread':
            count = notifications.update(is_read=False)
            message = f'Marked {count} notification(s) as unread'
        elif action == 'delete':
            count = notifications.count()
            notifications.delete()
            message = f'Deleted {count} notification(s)'
        else:
            return Response(
                {'error': 'Invalid action.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'message': message,
                'count': count
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def clear_all(self, request):
        """
        Delete all notifications for the current user.
        DELETE /api/notifications/clear_all/
        """
        count = Notification.objects.filter(recipient=request.user).delete()[0]
        
        return Response(
            {
                'message': f'Deleted all {count} notification(s)',
                'count': count
            },
            status=status.HTTP_200_OK
        )


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user's notification preferences.
    
    GET /api/notifications/preferences/ - Get notification preferences
    PATCH /api/notifications/preferences/ - Update notification preferences
    """
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create notification preferences for current user."""
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference
    
    def retrieve(self, request, *args, **kwargs):
        """Get user's notification preferences."""
        preference = self.get_object()
        serializer = self.get_serializer(preference)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update user's notification preferences."""
        partial = kwargs.pop('partial', False)
        preference = self.get_object()
        
        serializer = self.get_serializer(
            preference,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            {
                'message': 'Notification preferences updated successfully',
                'preferences': serializer.data
            },
            status=status.HTTP_200_OK
        )
