from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Follow, User
from .serializers import UserWithRecipesSerializer


class UserViewSet(viewsets.ModelViewSet):
    # ... базовые методы (me, avatar) ...

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        authors = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться от автора."""
        author = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            if request.user == author:
                return Response({'errors': 'Нельзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=request.user, author=author).exists():
                return Response({'errors': 'Уже подписан'}, status=status.HTTP_400_BAD_REQUEST)

            Follow.objects.create(user=request.user, author=author)
            serializer = UserWithRecipesSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Follow.objects.filter(user=request.user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Вы не подписаны'}, status=status.HTTP_400_BAD_REQUEST)