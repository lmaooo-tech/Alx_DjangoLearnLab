from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates password confirmation and creates a new user.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirm your password'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, data):
        """Validate that passwords match."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """Create and return a new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        # Create token for the new user
        Token.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Authenticates user based on username and password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Authenticate the user."""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError(
                "Must provide both username and password."
            )

        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    """
    Serializer for token response.
    Returns the authentication token for the user.
    """
    token = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """Return user details."""
        user = obj.get('user')
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    Displays user profile information.
    """
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'followers_count', 'following_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_followers_count(self, obj):
        """Return the count of followers."""
        return obj.followers.count()

    def get_following_count(self, obj):
        """Return the count of users this user is following."""
        return obj.following.count()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Allows users to update their bio and profile picture.
    """
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'profile_picture')
