from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from nested_admin.nested import NestedTabularInline, NestedModelAdmin

from tests.models import Test, Question, Answer, Result, Comment, MyUser


class AnswerInline(NestedTabularInline):
    model = Answer

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            if obj.answer_set.count():
                extra = 4 - obj.answer_set.count()
            else:
                extra = 4
        else:
            extra = 4
        return extra


class QuestionInline(NestedTabularInline):
    model = Question

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            if obj.question_set.count():
                extra = 5 - obj.question_set.count()
            else:
                extra = 5
        else:
            extra = 5
        return extra

    inlines = [AnswerInline, ]


class TestAdmin(NestedModelAdmin):
    list_display = ('title', 'author', 'date')
    fieldsets = [
        ('Test', {'fields': ['title', 'author', 'description']}),
    ]
    inlines = [QuestionInline, ]


class ResultAdmin(admin.ModelAdmin):
    list_display = ('author', 'test', 'mark', 'date')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('test', 'text', 'author')


class ResultInline(admin.TabularInline):
    model = Result
    readonly_fields = ('test', 'mark', 'date')
    exclude = ('answer', )
    extra = 0


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
admin.site.register(Result, ResultAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(MyUser, MyUserAdmin)
