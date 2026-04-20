from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Tag, Ingredient, Recipe, Favorite,
    ShoppingCart, IngredientInRecipe
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeListSerializer,
    RecipeCreateSerializer, RecipeMinifiedSerializer
)
from .pagination import CustomPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return super().get_queryset()


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self._add_to_list(Favorite, request.user, pk)
        return self._remove_from_list(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self._add_to_list(ShoppingCart, request.user, pk)
        return self._remove_from_list(ShoppingCart, request.user, pk)

    def _add_to_list(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_list(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепта нет в списке'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Выгрузка файла со списком ингредиентов из корзины."""
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        content = 'Список покупок:\n\n'
        for item in ingredients:
            content += (
                f"• {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        """Получение короткой ссылки на рецепт"""
        recipe = get_object_or_404(Recipe, id=pk)
        base_url = request.build_absolute_uri('/')
        short_link = f"{base_url.rstrip('/')}/s/{recipe.id}"
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
