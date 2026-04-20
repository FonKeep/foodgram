from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .serializers import UserWithRecipesSerializer, AvatarSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return UserWithRecipesSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user)

        # 1. Сериализуем авторов
        serializer = UserWithRecipesSerializer(
            authors, many=True, context={'request': request}
        )

        # 2. ВРУЧНУЮ собираем структуру пагинации, которую ждет фронтенд
        custom_response_data = {
            "count": authors.count(),
            "next": None,
            "previous": None,
            "results": serializer.data # Кладем наш идеальный JSON сюда
        }

        return Response(custom_response_data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Follow.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.avatar = serializer.validated_data['avatar']
        user.save()

        return Response(
            {'avatar': user.avatar.url},
            status=status.HTTP_200_OK
        )