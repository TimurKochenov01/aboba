from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import UserPhoto, UserInteraction, ViewHistory, Match, DateInvitation, UserLikeHistory
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Генерация моковых данных для тестирования'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=1000, help='Количество пользователей')
        parser.add_argument('--interactions', type=int, default=5000, help='Количество взаимодействий')

    def handle(self, *args, **options):
        fake = Faker('ru_RU')
        
        self.stdout.write('Генерация моковых данных...')
        
        users_count = options['users']
        interactions_count = options['interactions']
        
        cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
        hobbies_list = [
            'Путешествия, фотография, музыка',
            'Спорт, книги, кино',
            'Программирование, видеоигры',
            'Искусство, театр, танцы',
            'Кулинария, вино, рестораны'
        ]
        
        users = []
        for i in range(users_count):
            user = User(
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=random.choice(['M', 'F']),
                age=random.randint(18, 65),
                city=random.choice(cities),
                hobbies=random.choice(hobbies_list),
                status=random.choice(['looking', 'busy', 'complicated']),
                privacy_settings=random.choice(['public', 'private', 'friends_only']),
                is_active=True
            )
            user.set_password('password123')
            users.append(user)
        
        User.objects.bulk_create(users, batch_size=100)
        self.stdout.write(f'Создано {users_count} пользователей')
        
        created_users = User.objects.all()
        
        interactions = []
        for i in range(interactions_count):
            from_user = random.choice(created_users)
            to_user = random.choice([u for u in created_users if u != from_user])
            
            interaction = UserInteraction(
                from_user=from_user,
                to_user=to_user,
                interaction_type=random.choice(['like', 'dislike']),
                created_at=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.utc)
            )
            interactions.append(interaction)
        
        UserInteraction.objects.bulk_create(interactions, ignore_conflicts=True, batch_size=100)
        self.stdout.write(f'Создано {interactions_count} взаимодействий')
        
        self.stdout.write(
            self.style.SUCCESS('Моковые данные успешно сгенерированы!')
        )