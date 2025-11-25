from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Dating Platform API",
        default_version='v1',
        description="API для платформы знакомств",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'interactions', views.UserInteractionViewSet, basename='interaction')
router.register(r'view-history', views.ViewHistoryViewSet, basename='view-history')
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'date-invitations', views.DateInvitationViewSet, basename='date-invitation')
router.register(r'like-history', views.UserLikeHistoryViewSet, basename='like-history')
router.register(r'auth', views.UserRegistrationViewSet, basename='auth')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
