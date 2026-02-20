from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        return data

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userprofile.role', read_only=True)

    class Meta:
        model = User
        # WE EXPLICITLY INCLUDE first_name AND last_name
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile details (User model fields + Avatar).
    """
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    avatar = serializers.ImageField(source='userprofile.avatar', required=False)
    new_password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'new_password']

    def update(self, instance, validated_data):
        # Update User model fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        
        # Update password if provided
        new_password = validated_data.get('new_password')
        if new_password:
            instance.set_password(new_password)
            
        instance.save()

        # Update UserProfile fields (avatar)
        profile_data = validated_data.get('userprofile', {})
        avatar = profile_data.get('avatar')
        
        if avatar:
            # Ensure profile exists
            if hasattr(instance, 'userprofile'):
                instance.userprofile.avatar = avatar
                instance.userprofile.save()
            
        return instance
