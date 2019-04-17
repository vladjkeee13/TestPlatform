from django import forms

from tests.models import Test, Question, Answer, Comment, MyUser


class SearchForm(forms.Form):

    DATE_CHOICES = (
        (0, '-----------------'),
        (1, 'Сортировать по дате добавления'),
        (2, 'Сортировать в обратном порядке')
    )

    PASSED_CHOICES = (
        (0, '-----------------'),
        (1, 'Пройденные'),
        (2, 'Не пройденные')
    )

    title = forms.CharField(required=False)
    date = forms.ChoiceField(choices=DATE_CHOICES, required=False)
    passed = forms.ChoiceField(choices=PASSED_CHOICES, required=False)

    def _filter_by_title(self, queryset, user):

        return queryset.filter(
                title__icontains=self.cleaned_data['title']
            )

    def _filter_by_date(self, queryset, user):

        if int(self.cleaned_data['date']) == 1:
            queryset = queryset.order_by('-date')
        elif int(self.cleaned_data['date']) == 2:
            queryset = queryset.order_by('date')

        return queryset

    def _filter_by_passed(self, queryset, user):

        if int(self.cleaned_data['passed']) == 1:
            queryset = queryset.filter(result__author=user)
        elif int(self.cleaned_data['passed']) == 2:
            queryset = queryset.all().exclude(result__author=user)

        return queryset

    def get_searched_queryset(self, queryset, user):

        for field_name in self.fields:
            if field_name in self.cleaned_data and self.cleaned_data[field_name]:
                queryset = getattr(self, f'_filter_by_{field_name}')(queryset, user)

        return queryset


class AddTestForm(forms.ModelForm):

    class Meta:
        model = Test
        fields = ('title', 'description')
        widgets = {
            'description': forms.widgets.Textarea(attrs={'class': 'textarea', 'rows': 4})
        }

    def clean_title(self):

        title = self.cleaned_data['title']

        tests = Test.objects.all()

        for test in tests:
            if title == test.title:
                raise forms.ValidationError("Тест с таким именем уже существует!")

        return title

    def save(self, *args, **kwargs):

        user = kwargs.pop('user')
        test = super().save(commit=False)
        test.author = user
        test.save()

        return test


class AddQuestionForm(forms.Form):

    question = forms.CharField(required=True)
    current_answer = forms.CharField(required=True)
    answer1 = forms.CharField(required=True)
    answer2 = forms.CharField(required=True)
    answer3 = forms.CharField(required=True)
    answer4 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):

        self.test = kwargs.pop('test', None)
        super(AddQuestionForm, self).__init__(*args, **kwargs)

    def clean_question(self):

        question = self.cleaned_data['question']

        for quest in self.test.question.all():
            if question == quest.question_text:
                raise forms.ValidationError("Вопрос с таким именем уже существует!")

        return question

    def clean(self):

        cleaned_data = self.cleaned_data

        dict_of_answer = {
            'answer1': cleaned_data['answer1'],
            'answer2': cleaned_data['answer2'],
            'answer3': cleaned_data['answer3'],
            'answer4': cleaned_data['answer4']
        }

        if cleaned_data['current_answer'] not in dict_of_answer.values():
            self.add_error('current_answer', 'Введите правильный ответ!')

        for answer in dict_of_answer:

            new_answer_dict = dict_of_answer.copy()
            new_answer_dict.pop(answer)

            for a in new_answer_dict:
                if dict_of_answer[answer] == new_answer_dict[a]:
                    self.add_error(answer, 'Вы ввели несколько одинаковых ответов!')

        return cleaned_data

    def save(self, test):

        question = Question.objects.create(
            question_text=self.cleaned_data['question'],
            correct_answer=self.cleaned_data['current_answer']
        )

        dict_of_answers = [
            self.cleaned_data['answer1'],
            self.cleaned_data['answer2'],
            self.cleaned_data['answer3'],
            self.cleaned_data['answer4']
        ]

        for answer in dict_of_answers:
            Answer.objects.create(answer_text=answer, question=question)

        test.question.add(question)

        return test


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.widgets.Textarea(attrs={'class': 'textarea', 'rows': 4})
        }

    def save(self, *args, **kwargs):

        user = kwargs.pop('user')
        test = kwargs.pop('test')

        comment = super().save(commit=False)

        comment.author = user
        comment.test = test

        comment.save()

        return comment


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password_check = forms.CharField(widget=forms.PasswordInput)

    class Meta:

        model = MyUser
        fields = ('username', 'password', 'password_check', 'first_name', 'last_name', 'email', 'date_of_birth',
                  'personal_information', 'avatar')
        help_texts = {
            'username': None,
        }

    def clean(self):

        cleaned_data = self.cleaned_data

        username = cleaned_data['username']
        password = cleaned_data['password']
        password_check = cleaned_data['password_check']
        email = cleaned_data['email']

        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже зарегестрирован!')

        if password != password_check:
            raise forms.ValidationError('Пароли не совпадают!')

        if MyUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким емайлом уже зарегестрирован!')

        return cleaned_data

    def save(self, *args, **kwargs):

        user = super().save(commit=False)

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        date_of_birth = self.cleaned_data['date_of_birth']
        personal_information = self.cleaned_data['personal_information']
        avatar = self.cleaned_data['avatar']

        user.username = username
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.date_of_birth = date_of_birth
        user.personal_information = personal_information
        user.avatar = avatar

        user.save()

        return user


class LoginForm(forms.Form):

    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    def clean(self):

        cleaned_data = self.cleaned_data

        username = cleaned_data['username']
        password = cleaned_data['password']

        if not MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем не зарегестрирован!')

        user = MyUser.objects.get(username=username)

        if user and not user.check_password(password):
            raise forms.ValidationError('Не верный пароль!')

        return cleaned_data
