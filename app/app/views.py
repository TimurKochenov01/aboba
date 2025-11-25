from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
import random

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().prefetch_related('photos')
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'city', 'status']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.action == 'list':
            age_min = self.request.query_params.get('age_min')
            age_max = self.request.query_params.get('age_max')
            
            if age_min:
                queryset = queryset.filter(age__gte=age_min)
            if age_max:
                queryset = queryset.filter(age__lte=age_max)
        
        return queryset.exclude(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def random_profile(self, request):
        """Получить случайный профиль с фильтрацией"""
        queryset = self.get_queryset()
        
        filters = {}
        gender = request.query_params.get('gender')
        age_min = request.query_params.get('age_min')
        age_max = request.query_params.get('age_max')
        city = request.query_params.get('city')
        status = request.query_params.get('status')
        
        if gender:
            filters['gender'] = gender
        if age_min:
            filters['age__gte'] = age_min
        if age_max:
            filters['age__lte'] = age_max
        if city:
            filters['city__iexact'] = city
        if status:
            filters['status'] = status
        
        filtered_users = queryset.filter(**filters)
        
        if not filtered_users.exists():
            return Response({"detail": "Нет пользователей, соответствующих фильтрам"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        random_user = random.choice(list(filtered_users))
        serializer = self.get_serializer(random_user)
        
        ViewHistory.objects.create(
            viewer=request.user,
            viewed_user=random_user
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        user = self.get_object()
        if user != request.user:
            return Response({"detail": "Недостаточно прав"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        photo = request.FILES.get('photo')
        is_main = request.data.get('is_main', False)
        
        if not photo:
            return Response({"detail": "Фото не предоставлено"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user_photo = UserPhoto.objects.create(
            user=user,
            photo=photo,
            is_main=is_main
        )
        
        return Response(UserPhotoSerializer(user_photo).data, 
                      status=status.HTTP_201_CREATED)

class UserInteractionViewSet(viewsets.ModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    
    def get_queryset(self):
        return UserInteraction.objects.filter(from_user=self.request.user)\
                   .select_related('to_user', 'to_user__photos')
    
    def perform_create(self, serializer):
        to_user_id = self.request.data.get('to_user')
        interaction_type = self.request.data.get('interaction_type')
        
        if UserInteraction.objects.filter(from_user=self.request.user, to_user_id=to_user_id).exists():
            raise serializers.ValidationError("Взаимодействие уже существует")
        
        interaction = serializer.save(from_user=self.request.user)
        
        if interaction_type == 'like':
            to_user = User.objects.get(id=to_user_id)
            to_user.likes_count += 1
            to_user.save()
            
            UserLikeHistory.objects.create(
                user=to_user,
                liked_by=self.request.user
            )
            
            if UserInteraction.objects.filter(
                from_user=to_user, 
                to_user=self.request.user, 
                interaction_type='like'
            ).exists():
                Match.objects.create(
                    user1=self.request.user,
                    user2=to_user
                )

class ViewHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ViewHistorySerializer
    
    def get_queryset(self):
        return ViewHistory.objects.filter(viewer=self.request.user)\
                   .select_related('viewed_user', 'viewed_user__photos')\
                   .order_by('-viewed_at')

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchSerializer
    
    def get_queryset(self):
        return Match.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user),
            is_active=True
        ).select_related('user1', 'user2', 'user1__photos', 'user2__photos')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class DateInvitationViewSet(viewsets.ModelViewSet):
    queryset = DateInvitation.objects.all()
    serializer_class = DateInvitationSerializer
    
    def get_queryset(self):
        return DateInvitation.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        ).select_related('from_user', 'to_user', 'match')
    
    def perform_create(self, serializer):
        match_id = self.request.data.get('match')
        try:
            match = Match.objects.get(id=match_id)
            if self.request.user not in [match.user1, match.user2]:
                raise serializers.ValidationError("Вы не участник этого матча")
            
            to_user = match.user2 if match.user1 == self.request.user else match.user1
            serializer.save(from_user=self.request.user, to_user=to_user, match=match)
        except Match.DoesNotExist:
            raise serializers.ValidationError("Матч не найден")

class UserLikeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserLikeHistorySerializer
    
    def get_queryset(self):
        return UserLikeHistory.objects.filter(user=self.request.user)\
                   .select_related('liked_by', 'liked_by__photos')\
                   .order_by('-created_at')

class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "user": UserProfileSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно зарегистрирован"
        }, status=status.HTTP_201_CREATED)