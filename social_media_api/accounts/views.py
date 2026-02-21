from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404

from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    TokenSerializer,
    UserDetailSerializer,
    UserProfileUpdateSerializer,
    FollowSerializer,
    FollowingListSerializer,
    FollowersListSerializer,
    FollowActionResponseSerializer
)

# Base classes available: generics.GenericAPIView for advanced customization


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    POST /api/auth/register/
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token = Token.objects.get(user=user)
        
        return Response(
            {
                'message': 'User registered successfully',
                'user': UserDetailSerializer(user).data,
                'token': token.key
            },
            status=status.HTTP_201_CREATED
        )


class UserLoginView(generics.CreateAPIView):
    """
    API view for user login.
    POST /api/auth/login/
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle user login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data.get('user')
        token, created = Token.objects.get_or_create(user=user)
        
        return Response(
            {
                'message': 'Login successful',
                'token': token.key,
                'user': UserDetailSerializer(user).data
            },
            status=status.HTTP_200_OK
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.
    GET /api/auth/profile/ - Get current user profile
    PATCH/PUT /api/auth/profile/ - Update current user profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Handle profile update."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserProfileUpdateSerializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                'message': 'Profile updated successfully',
                'user': UserDetailSerializer(instance).data
            },
            status=status.HTTP_200_OK
        )


class UserDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving a specific user's profile.
    GET /api/auth/users/<user_id>/ - Get user profile by ID
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API view for user logout.
    POST /api/auth/logout/
    Deletes the user's authentication token.
    """
    try:
        # Delete the token associated with the user
        token = Token.objects.get(user=request.user)
        token.delete()
        
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return Response(
            {'error': 'Token not found'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving users, with follow/unfollow actions.
    GET /api/users/ - List all users
    GET /api/users/<user_id>/ - Get user by ID
    POST /api/users/<user_id>/follow/ - Follow a user
    POST /api/users/<user_id>/unfollow/ - Unfollow a user
    GET /api/users/<user_id>/followers/ - Get list of followers
    GET /api/users/<user_id>/following/ - Get list of users being followed
    GET /api/users/me/following/ - Get current user's following list
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'follow':
            return FollowSerializer
        elif self.action == 'unfollow':
            return FollowSerializer
        elif self.action == 'following':
            return FollowingListSerializer
        elif self.action == 'followers':
            return FollowersListSerializer
        return UserDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, id=None):
        """
        Follow a user.
        POST /api/users/<user_id>/follow/
        """
        target_user = self.get_object()
        
        # Prevent user from following themselves
        if request.user == target_user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add the current user to the target user's followers
        if target_user.followers.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        target_user.followers.add(request.user)
        
        return Response(
            {
                'message': f'You are now following {target_user.username}',
                'status': 'following',
                'user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'email': target_user.email,
                },
                'followers_count': target_user.followers.count(),
                'following_count': target_user.following.count(),
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, id=None):
        """
        Unfollow a user.
        POST /api/users/<user_id>/unfollow/
        """
        target_user = self.get_object()
        
        # Prevent user from unfollowing themselves
        if request.user == target_user:
            return Response(
                {'error': 'You cannot unfollow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove the current user from the target user's followers
        if not target_user.followers.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        target_user.followers.remove(request.user)
        
        return Response(
            {
                'message': f'You have unfollowed {target_user.username}',
                'status': 'not_following',
                'user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'email': target_user.email,
                },
                'followers_count': target_user.followers.count(),
                'following_count': target_user.following.count(),
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def followers(self, request, id=None):
        """
        Get list of followers for a user.
        GET /api/users/<user_id>/followers/
        """
        user = self.get_object()
        followers = user.followers.all()
        
        serializer = self.get_serializer(
            followers,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': followers.count(),
                'user': user.username,
                'followers': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def following(self, request, id=None):
        """
        Get list of users that a user is following.
        GET /api/users/<user_id>/following/
        """
        user = self.get_object()
        following = user.following.all()
        
        serializer = self.get_serializer(
            following,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': following.count(),
                'user': user.username,
                'following': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_following(self, request):
        """
        Get the current user's following list.
        GET /api/users/me/following/
        """
        user = request.user
        following = user.following.all()
        
        serializer = self.get_serializer(
            following,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': following.count(),
                'user': user.username,
                'following': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_followers(self, request):
        """
        Get the current user's followers list.
        GET /api/users/me/followers/
        """
        user = request.user
        followers = user.followers.all()
        
        serializer = self.get_serializer(
            followers,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': followers.count(),
                'user': user.username,
                'followers': serializer.data
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user_view(request, user_id):
    """
    API view for following a user using a simple POST request.
    POST /api/auth/users/<user_id>/follow/
    """
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Prevent user from following themselves
    if request.user == target_user:
        return Response(
            {'error': 'You cannot follow yourself.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already following
    if target_user.followers.filter(id=request.user.id).exists():
        return Response(
            {'error': 'You are already following this user.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    target_user.followers.add(request.user)
    
    return Response(
        {
            'message': f'You are now following {target_user.username}',
            'status': 'following',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
            },
            'followers_count': target_user.followers.count(),
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user_view(request, user_id):
    """
    API view for unfollowing a user using a simple POST request.
    POST /api/auth/users/<user_id>/unfollow/
    """
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Prevent user from unfollowing themselves
    if request.user == target_user:
        return Response(
            {'error': 'You cannot unfollow yourself.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if not following
    if not target_user.followers.filter(id=request.user.id).exists():
        return Response(
            {'error': 'You are not following this user.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    target_user.followers.remove(request.user)
    
    return Response(
        {
            'message': f'You have unfollowed {target_user.username}',
            'status': 'not_following',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
            },
            'followers_count': target_user.followers.count(),
        },
        status=status.HTTP_200_OK
    )

