from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTest(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='test_username_1')
        user_2 = User.objects.create(username='test_username_2')
        user_3 = User.objects.create(username='test_username_3')

        book_1 = Book.objects.create(name='test_book_test_1', price=100, author_name='a')
        book_2 = Book.objects.create(name='test_book_test_2', price=90, author_name='b')

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, rate=4)
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, rate=4)
        UserBookRelation.objects.create(user=user_3, book=book_1, like=True)

        books = Book.objects.all().annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('id')
        data = BookSerializer(books, many=True).data
        print(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': 'test_book_test_1',
                'price': '100.00',
                'author_name': 'a',
                'owner': None,
                'likes_count': 3,
                'annotated_likes': 3,
                'annotated_rating': '4.00',
            },
            {
                'id': book_2.id,
                'name': 'test_book_test_2',
                'price': '90.00',
                'author_name': 'b',
                'owner': None,
                'likes_count': 0,
                'annotated_likes': 0,
                'annotated_rating': None,
            }
        ]

        self.assertEqual(expected_data, data)
