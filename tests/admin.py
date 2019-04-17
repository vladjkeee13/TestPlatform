from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tests.models import Test, Question, Answer, Result, Comment, MyUser


class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author' ,'date')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'correct_answer')


class ResultAdmin(admin.ModelAdmin):
    list_display = ('author', 'test', 'mark', 'date')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('test', 'text', 'author')


class ResultInline(admin.TabularInline):
    model = Result
    readonly_fields = ('test', 'mark', 'date')


class MyUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 'date_of_birth',
                                         'personal_information')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [ResultInline]


admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(MyUser, MyUserAdmin)
