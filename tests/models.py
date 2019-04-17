from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models


class Test(models.Model):

    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    question = models.ManyToManyField('tests.Question')
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    number_of_passes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Question(models.Model):

    question_text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class Answer(models.Model):

    answer_text = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.answer_text


class Result(models.Model):

    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    mark = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}:{}'.format(self.test, self.mark)


class Comment(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)


class MyUser(AbstractUser):

    avatar = models.ImageField(blank=True, null=True, upload_to='avatars')
    date_of_birth = models.DateField(blank=True, null=True)
    personal_information = models.TextField(blank=True, null=True)
