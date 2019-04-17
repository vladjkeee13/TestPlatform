from django.urls import path

from tests.views import HomeView, TestView, ResultView, PassingTheTestView, AddTestView, AddQuestionView, \
    TestAddedView, AddCommentView

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('test/<str:test_title>/', TestView.as_view(), name='test'),
    path('passing-the-test/<str:test_title>/', PassingTheTestView.as_view(), name='passing-the-test'),
    path('test/<str:test_title>/result/', ResultView.as_view(), name='result'),
    path('add-test/', AddTestView.as_view(), name='add-test'),
    path('<str:test_name>/add-question/', AddQuestionView.as_view(), name='add-question'),
    path('<str:test_name>/added', TestAddedView.as_view(), name='test-added'),
    path('<str:test_name>/add-comment/', AddCommentView.as_view(), name='add-comment')
]
