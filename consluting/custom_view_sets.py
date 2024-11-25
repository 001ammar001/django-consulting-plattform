from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

class ListOnlyViewSet(mixins.ListModelMixin,GenericViewSet):
    pass

class ListCreateViewSet(mixins.CreateModelMixin,mixins.ListModelMixin,GenericViewSet):
    pass

class ListCreateDestroyViewSet(mixins.CreateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,GenericViewSet):
    pass