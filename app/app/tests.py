from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, UserInteraction, Match

class UserInteractionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            password='password123',
            first_name='John',
            last_name='Doe',
            gender='M',
            age=25,
            city='Moscow'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            password='password123',
            first_name='Jane',
            last_name='Doe',
            gender='F',
            age=23,
            city='Moscow'
        )
        
        self.client.force_authenticate(user=self.user1)

    def test_like_user(self):
        url = reverse('interaction-list')
        data = {
            'to_user': self.user2.id,
            'interaction_type': 'like'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserInteraction.objects.count(), 1)
        
        interaction = UserInteraction.objects.first()
        self.assertEqual(interaction.interaction_type, 'like')
        self.assertEqual(interaction.from_user, self.user1)
        self.assertEqual(interaction.to_user, self.user2)

    def test_dislike_user(self):
        url = reverse('interaction-list')
        data = {
            'to_user': self.user2.id,
            'interaction_type': 'dislike'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserInteraction.objects.first().interaction_type, 'dislike')

    def test_mutual_like_creates_match(self):
        interaction1 = UserInteraction.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            interaction_type='like'
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse('interaction-list')
        data = {
            'to_user': self.user1.id,
            'interaction_type': 'like'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(Match.objects.filter(user1=self.user1, user2=self.user2).exists())

    def test_cannot_interact_with_same_user_twice(self):
        UserInteraction.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            interaction_type='like'
        )
        
        url = reverse('interaction-list')
        data = {
            'to_user': self.user2.id,
            'interaction_type': 'dislike'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User',
            gender='M',
            age=30,
            city='Moscow'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@test.com')
        self.assertEqual(response.data['first_name'], 'Test')