import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    # Setup for tests: user auth, objects
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='test_book_test_1', owner=self.user, price=100, author_name='a')
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=4)
        self.book_2 = Book.objects.create(name='test_book_test_2', owner=self.user, price=90, author_name='b')
        self.book_3 = Book.objects.create(name='test_book_test_3', owner=self.user, price=80, author_name='c')
        self.book_4 = Book.objects.create(name='test_book_test_4', owner=self.user, price=60, author_name='d')
        self.book_5 = Book.objects.create(name='test_book_test_5_a', owner=self.user, price=60, author_name='e')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)

        books = Book.objects.all().annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(serializer.data[0]['annotated_likes'], 1)
        self.assertEqual(serializer.data[0]['annotated_likes'], 1)
        self.assertEqual(serializer.data[0]['annotated_rating'], '4.00')

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 60})

        books = Book.objects.filter(id__in=[self.book_4.id, self.book_5.id]).annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'a'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_5.id]).annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-author_name'})
        books = Book.objects.filter(id__in=[self.book_5.id, self.book_4.id, self.book_3.id, self.book_2.id, self.book_1.id]).annotate(
            annotated_likes=Count((Case(When(userbookrelation__like=True, then=1)))),
            annotated_rating=Avg('userbookrelation__rate')
        ).order_by('-author_name')
        serializer = BookSerializer(books, many=True)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer.data, response.data)

    def test_create(self):
        self.assertEqual(5, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "api_test_book",
            "price": "100.00",
            "author_name": "api_test_author"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(6, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        self.assertEqual(5, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

    def test_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        self.assertEqual(5, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(5, Book.objects.all().count())

    def test_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        self.assertEqual(5, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Book.objects.all().count())


class BooksRelationsTestCase(APITestCase):
    # Setup for tests: user auth, objects
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user_2 = User.objects.create(username='test_username_2')
        self.book_1 = Book.objects.create(name='test_book_test_1', owner=self.user, price=100, author_name='a')
        self.book_2 = Book.objects.create(name='test_book_test_2', owner=self.user, price=90, author_name='b')

    def test_like_bookmark(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            "bookmarks": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)

        self.assertEqual(3, relation.rate)
