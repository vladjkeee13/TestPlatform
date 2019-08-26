from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, FormView, CreateView, DetailView

from tests.forms import SearchForm, AddTestForm, AddQuestionForm, AddCommentForm, RegistrationForm, LoginForm
from tests.models import Test, Answer, Question, Result, MyUser


class HomeView(ListView):

    template_name = 'home_page.html'
    model = Test

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.GET:
            form = SearchForm(data=self.request.GET)
            if form.is_valid():
                context['object_list'] = form.get_searched_queryset(context['object_list'], user=self.request.user)
            context['form'] = form
        else:
            context['form'] = SearchForm()

        return context


class TestView(DetailView):

    template_name = 'test.html'
    model = Test

    def get_object(self, queryset=None):

        title = self.kwargs.get('test_title')
        return get_object_or_404(self.model, title=title)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        test = self.get_object()
        context['test'] = test

        try:
            result = Result.objects.get(test=test, author=self.request.user)

            def percent(mark, total):
                return mark * 100 / total

            context['result'] = result
            context['percent'] = percent(result.mark, result.test.question_set.count())
        except:
            pass

        return context


@method_decorator(login_required, name='dispatch')
class PassingTheTestView(ListView):

    template_name = 'passing_the_test.html'
    model = Question
    paginate_by = 1

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        test = Test.objects.get(title=self.kwargs['test_title'])
        context['test'] = test

        if 'answer_id' in self.request.GET:
            result, created = Result.objects.get_or_create(test=test, author=self.request.user)
            result.answer.add(Answer.objects.get(id=self.request.GET['answer_id']))

        return context

    def get_queryset(self):

        test = Test.objects.get(title=self.kwargs['test_title'])
        queryset = Question.objects.filter(test=test)

        return queryset


@method_decorator(login_required, name='dispatch')
class ResultView(TemplateView):

    template_name = 'result.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        test = Test.objects.get(title=self.kwargs['test_title'])
        context['test'] = test

        result, created = Result.objects.get_or_create(test=test, author=self.request.user)
        result.answer.add(Answer.objects.get(id=self.request.GET['answer_id']))

        context['result'] = result

        if not result.mark:
            for answer in result.answer.all():
                if answer.answer_text == Question.objects.get(answer=answer).correct_answer:
                    result.mark += 1
                    result.save()

        def percent(mark, total):
            total = len(total)
            return mark*100/total

        context['percent'] = round(percent(result.mark, result.answer.all()), 2)
        context['total'] = result.answer.count()

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class AddTestView(CreateView):

    template_name = 'add_test.html'
    form_class = AddTestForm

    def form_valid(self, form):

        response = super().form_valid(form)
        self.object = form.save(user=self.request.user)

        return response


@method_decorator(login_required, name='dispatch')
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
        test = context.get('test')
        form.save(test=test)

        if 'test-end' not in self.request.POST:
            return redirect('tests:add-question', test_name=self.kwargs['test_name'])
        else:
            return redirect('tests:test-added', test_name=self.kwargs['test_name'])

    def form_invalid(self, form, **kwargs):

        context = self.get_context_data(**kwargs)

        context['check_all_answers_and_correct_answer_and_question'] = form['question'].errors and form['current_answer'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)
        context['check_all_answers_and_correct_answer'] = form['current_answer'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)
        context['check_correct_answer_and_question'] = form['question'].errors and (form['answer1'].errors or form['answer2'].errors or form['answer3'].errors or form['answer4'].errors)

        return self.render_to_response(context)


@method_decorator(login_required, name='dispatch')
class TestAddedView(TemplateView):

    template_name = 'test_added.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data()

        test = Test.objects.get(title=kwargs['test_name'])

        context['test'] = test

        return context


@method_decorator(login_required, name='dispatch')
class AddCommentView(CreateView):

    template_name = 'add_comment.html'
    form_class = AddCommentForm

    def form_valid(self, form):

        response = super().form_valid(form)
        test = Test.objects.get(title=self.kwargs['test_name'])
        self.object = form.save(user=self.request.user, test=test)

        return response

    def get_success_url(self):
        return reverse('tests:test', kwargs={'test_title': self.kwargs.get('test_name')})


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


@method_decorator(login_required, name='dispatch')
class MyAccountView(TemplateView):

    template_name = 'my_account.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data()

        context['user'] = self.request.user

        return context
