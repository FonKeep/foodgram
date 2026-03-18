from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe

User = get_user_model()

class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками (UserWithRecipes в OpenAPI)."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        # Импорт здесь во избежание циклической зависимости
        from recipes.serializers import RecipeMinifiedSerializer
        return RecipeMinifiedSerializer(recipes, many=True).data