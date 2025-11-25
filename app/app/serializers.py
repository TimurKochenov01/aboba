from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import *

class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ['id', 'photo', 'is_main', 'uploaded_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name', 
                 'gender', 'age', 'city', 'hobbies']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    photos = UserPhotoSerializer(many=True, read_only=True)
    main_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'age', 'city', 
                 'hobbies', 'status', 'likes_count', 'privacy_settings', 'photos', 'main_photo']
        read_only_fields = ['email', 'likes_count']
    
    def get_main_photo(self, obj):
        main_photo = obj.photos.filter(is_main=True).first()
        if main_photo:
            return UserPhotoSerializer(main_photo).data
        return None

class UserInteractionSerializer(serializers.ModelSerializer):
    to_user_profile = UserProfileSerializer(source='to_user', read_only=True)
    
    class Meta:
        model = UserInteraction
        fields = ['id', 'to_user', 'to_user_profile', 'interaction_type', 'created_at']
        read_only_fields = ['from_user', 'created_at']

class ViewHistorySerializer(serializers.ModelSerializer):
    viewed_user_profile = UserProfileSerializer(source='viewed_user', read_only=True)
    
    class Meta:
        model = ViewHistory
        fields = ['id', 'viewed_user', 'viewed_user_profile', 'viewed_at']

class MatchSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'other_user', 'created_at', 'is_active']
    
    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other_user = obj.user2 if obj.user1 == request.user else obj.user1
            return UserProfileSerializer(other_user).data
        return None

class DateInvitationSerializer(serializers.ModelSerializer):
    from_user_profile = UserProfileSerializer(source='from_user', read_only=True)
    to_user_profile = UserProfileSerializer(source='to_user', read_only=True)
    
    class Meta:
        model = DateInvitation
        fields = ['id', 'match', 'from_user', 'from_user_profile', 'to_user', 'to_user_profile',
                 'message', 'proposed_date', 'status', 'created_at']
        read_only_fields = ['from_user', 'created_at']

class UserLikeHistorySerializer(serializers.ModelSerializer):
    liked_by_profile = UserProfileSerializer(source='liked_by', read_only=True)
    
    class Meta:
        model = UserLikeHistory
        fields = ['id', 'liked_by', 'liked_by_profile', 'created_at']