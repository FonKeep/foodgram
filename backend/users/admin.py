from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    ordering = ('email',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
