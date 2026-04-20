from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),                  # 1. Ваш кастомный UserViewSet
    path('auth/', include('djoser.urls.authtoken')), # 2. Логин/Логаут
    path('', include('djoser.urls')),                 # 3. Базовый Djoser (регистрация и др.)
]