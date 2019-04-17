from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, FormView

from tests.forms import SearchForm, AddTestForm, AddQuestionForm, AddCommentForm, RegistrationForm, LoginForm
from tests.models import Test, Answer, Question, Result, MyUser


class HomeView(ListView):

    template_name = 'home_page.html'
    model = Test

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.GET:
            context['form'] = SearchForm(data=self.request.GET)
            if context['form'].is_valid():
                context['object_list'] = context['form'].get_searched_queryset(context['object_list'], user=self.request.user)
        else:
            context['form'] = SearchForm()

        return context


class TestView(TemplateView):

    template_name = 'test.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        test = Test.objects.get(title=self.kwargs['test_title'])

        try:
            result = Result.objects.get(test=test, author=self.request.user)

            def percent(mark, total):
                return mark * 100 / total

            context['result'] = result
            context['percent'] = percent(result.mark, result.test.question.count())
        except:
            'result not found'

        context['test'] = test

        return context


class PassingTheTestView(ListView):

    template_name = 'passing_the_test.html'
    model = Question

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        test = Test.objects.get(title=self.kwargs['test_title'])
        questions = Question.objects.filter(test=test)
        context['questions'] = questions
        context['test'] = test

        return context


class ResultView(TemplateView):

    template_name = 'result.html'

    def post(self, *args, **kwargs):

        answer_id_list = list(self.request.POST.values())[1:]
        test_title = self.kwargs['test_title']
        test = Test.objects.get(title=test_title)

        selected_answers = []
        correct_answers = []

        result = 0

        for answer_id in answer_id_list:
            answer = (Answer.objects.get(id=answer_id))
            selected_answers.append(answer.answer_text)
            correct_answers.append(answer.question.correct_answer)

        both_answers = list(zip(selected_answers, correct_answers))

        for elem in both_answers:
            if str(elem[0]) == str(elem[1]):
                result += 1

        def percent(mark, total):
            total = len(total)
            return mark*100/total

        Result.objects.create(test=test, author=self.request.user, mark=result)

        test.number_of_passes = test.number_of_passes + 1
        test.save()
        context = {
            'result': result,
            'total': len(answer_id_list),
            'percent': percent(result, correct_answers),
            'test': test
        }

        return super(TemplateView, self).render_to_response(context)


class AddTestView(FormView):

    template_name = 'add_test.html'
    form_class = AddTestForm

    def form_valid(self, form):

        form.save(user=self.request.user)

        return redirect('tests:add-question', test_name=self.request.POST['title'])


class AddQuestionView(FormView):

    template_name = 'add_question.html'
    form_class = AddQuestionForm

    def get_form_kwargs(self):

        kwargs = super(AddQuestionView, self).get_form_kwargs()
        kwargs['test'] = Test.objects.get(title=self.kwargs['test_name'])

        return kwargs

    def get_context_data(self, **kwargs):

        context = super().get_context_data()
        test = Test.objects.get(title=self.kwargs['test_name'])
        context['test'] = test

        return context

    def form_valid(self, form):

        context = self.get_context_data()
        form.save(test=context.get('test'))
        if context.get('test').question.all().count() > 4:
            return redirect('tests:test-added', test_name=self.kwargs['test_name'])
        else:
            return redirect('tests:add-question', test_name=self.kwargs['test_name'])

    def form_invalid(self, form, **kwargs):

        context = self.get_context_data(**kwargs)

        context['check_all_answers_and_correct_answer_and_question'] = form['question'].errors and form['current_answer'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)
        context['check_all_answers_and_correct_answer'] = form['current_answer'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)
        context['check_correct_answer_and_question'] = form['question'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)

        return self.render_to_response(context)


class TestAddedView(TemplateView):

    template_name = 'test_added.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data()

        test = Test.objects.get(title=kwargs['test_name'])

        context['test'] = test

        return context


class AddCommentView(FormView):

    template_name = 'add_comment.html'
    form_class = AddCommentForm

    def form_valid(self, form):

        test = Test.objects.get(title=self.kwargs['test_name'])
        form.save(user=self.request.user, test=test)

        return redirect('tests:test', test_title=self.kwargs['test_name'])


class RegistrationView(FormView):

    template_name = 'registration.html'
    form_class = RegistrationForm

    def form_valid(self, form, backend='django.contrib.auth.backends.ModelBackend'):

        form.save()

        user = MyUser.objects.get(username=form.cleaned_data['username'])

        if user:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect('/')


class LoginView(FormView):

    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        login_user = authenticate(username=username, password=password)

        if login_user:
            login(self.request, login_user)

        return redirect('/')


class MyAccountView(TemplateView):

    template_name = 'my_account.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data()

        context['user'] = self.request.user

        return context
