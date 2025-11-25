from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]
    
    STATUS_CHOICES = [
        ('looking', 'В поиске'),
        ('busy', 'Занят'),
        ('complicated', 'Все сложно'),
        ('married', 'Женат/Замужем'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Публичный'),
        ('private', 'Приватный'),
        ('friends_only', 'Только друзьям'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    city = models.CharField(max_length=100)
    hobbies = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='looking')
    likes_count = models.PositiveIntegerField(default=0)
    privacy_settings = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='user_photos/')
    is_main = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.is_main:
            UserPhoto.objects.filter(user=self.user, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

class UserInteraction(models.Model):
    INTERACTION_CHOICES = [
        ('like', 'Лайк'),
        ('dislike', 'Дизлайк'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_interactions')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_interactions')
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['from_user', 'to_user']),
            models.Index(fields=['to_user', 'interaction_type']),
        ]

class ViewHistory(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_profiles')
    viewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['viewer', 'viewed_at']),
        ]

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user1', 'user2']

class DateInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('cancelled', 'Отменено'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    message = models.TextField(blank=True)
    proposed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['match', 'status']),
        ]

class UserLikeHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_history')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]