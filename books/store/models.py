from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=1500)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=600)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='other_books')

    def __str__(self):
        return f'Id {self.id}: {self.name}'


class UserBookRelation(models.Model):
    CHOICES_OF_RATE = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False, null=True)
    bookmarks = models.BooleanField(default=False, null=True)
    rate = models.PositiveSmallIntegerField(choices=CHOICES_OF_RATE, null=True)

    def __str__(self):
        return f'USER: {self.user.username}   BOOK: {self.book.name}   RATE: {self.rate}'
