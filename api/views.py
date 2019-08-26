from rest_framework.viewsets import ModelViewSet

from api.serializers import TestSerializer
from tests.models import Test


class APITest(ModelViewSet):

    queryset = Test.objects.all().order_by('-id')
    serializer_class = TestSerializer
