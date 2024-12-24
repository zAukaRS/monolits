from django.contrib import admin
from .models import UserProfile, QuestionPost, Option, UserVote

admin.site.register(UserProfile)


@admin.register(QuestionPost)
class QuestionPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_active')

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'votes')

@admin.register(UserVote)
class UserVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'option', 'voted_at')