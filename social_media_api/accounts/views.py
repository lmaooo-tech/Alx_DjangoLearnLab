from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    TokenSerializer,
    UserDetailSerializer,
    UserProfileUpdateSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    POST /api/auth/register/
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    ViewSet for listing and retrieving users.
    GET /api/users/ - List all users
    GET /api/users/<user_id>/ - Get user by ID
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

