from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  # filters
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['book'])
        print('created', created)
        return obj


def auth(request):
    return render(request, 'oauth.html')
