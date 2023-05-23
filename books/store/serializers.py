from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BookSerializer(ModelSerializer):
    # Определения метода для функции с запрсом кол-ва лайков через фильтры
    likes_count = serializers.SerializerMethodField()
    # Определение сериализатора для запроса кол-ва лайков через аннотации
    annotated_likes = serializers.IntegerField(read_only=True)
    # Определение сериализатора для запроса средней оценки книги через аннотации
    annotated_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'owner', 'likes_count', 'annotated_likes', 'annotated_rating')

    # Функция с запросом кол-ва лайков у книги через метод filter
    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'bookmarks', 'rate')
