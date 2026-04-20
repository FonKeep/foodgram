from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from recipes.models import Recipe
from recipes.serializers import RecipeMinifiedSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)


class UserWithRecipesSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = None
        if request:
            limit = request.query_params.get('recipes_limit')

        recipes = Recipe.objects.filter(author=obj)

        if limit and str(limit).isdigit():
            recipes = recipes[:int(limit)]

        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context).data
