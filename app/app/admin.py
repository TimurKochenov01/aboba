from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'gender', 'age', 'city', 'status', 'likes_count']
    list_filter = ['gender', 'city', 'status', 'privacy_settings']
    search_fields = ['email', 'first_name', 'last_name', 'city']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('gender', 'age', 'city', 'hobbies', 'status', 'likes_count', 'privacy_settings')
        }),
    )

@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo', 'is_main', 'uploaded_at']
    list_filter = ['is_main', 'uploaded_at']
    search_fields = ['user__email']

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'interaction_type', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['from_user__email', 'to_user__email']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user1__email', 'user2__email']

admin.site.register(ViewHistory)
admin.site.register(DateInvitation)
admin.site.register(UserLikeHistory)