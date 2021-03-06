from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from datetime import date


# Genre model


class Genre(models.Model):
    """ Model representing a book genre."""
    name = models.CharField(max_length=200, help_text="Enter a book genre")

    class Meta:
        permissions = (("can_add", "Can add genres"),)

    def __str__(self):
        """String for representing the Model object"""
        return self.name


# Review model


# Book Model


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)"""
    title = models.CharField(max_length=200)
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 character unique identifier for a book')

    description = models.TextField(
        max_length=1000, help_text='Enter a brief summary', blank=True)

    cover_img = models.ImageField(
        upload_to='book_covers/', null=True, blank=True)
    publication_date = models.DateField(blank=True, default=date.today)
    # foreign key used because a book can only have one author, but authors can have written multiple books
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    # many to many field used because books can have many genres and genres can contain many books
    genre = models.ManyToManyField(
        Genre, help_text='Select a genre for this book')

    class Meta:
        permissions = (("can_edit", "Edit existing books"), ("can_add", "Can add new books"),
                       ('can_delete', "Can delete books"))

    def __str__(self):
        """ String representation of the Model object"""
        return self.title

    def get_absolute_url(self):
        """ Returns the url to access a detail record for this book"""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the genre, required to display genre in admin view"""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def at_least_one_bookinst_is_avail(self):
        book_insts = BookInstance.objects.filter(book=self)
        for inst in book_insts:
            if inst.status == 'a':
                return True
        return False

    def num_copies_avail(self):
        book_insts = BookInstance.objects.filter(book=self)
        num_avail = 0
        for book in book_insts:
            if book.status == 'a':
                num_avail += 1
        return num_avail

    def total_copies(self):
        return BookInstance.objects.filter(book=self).count()

    def average_review(self):
        reviews = Review.objects.filter(book=self)
        counter = 0
        summer = 0
        for review in reviews:
            summer += review.stars
            counter += 1
        if counter == 0:
            return -1
        return summer/counter

    # def display_num_of_reviews(self):
    #     """Create a string showing how many reviews a book has"""
    #     count = self.review.all().count()
    #     return count

    #display_num_of_reviews.short_description = "Number of Reviews"


class Review(models.Model):
    """ Model representing a book review"""
    writer = models.CharField(
        max_length=200, help_text='Enter author of review')
    body = models.TextField(max_length=2000, help_text='Review contents')
    stars = models.IntegerField(
        help_text='Enter how many stars the reviewer gave')

    date_written = models.DateField(
        default=date.today, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, null=True, related_name="reviews")

    class Meta:
        ordering = ['date_written']

    def __str__(self):
        """String representing the model object"""
        return self.body

    # def get_date_written(self):
    #     return date_written.date()


class BookInstance(models.Model):
    """ Model representing a specific copy of a book (that can be borrowed from the library)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this book")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    borrower = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    LOAN_STATUS = (
        ('a', 'Available'),
        ('r', 'Reserved'),
        ('o', 'Checked Out'),
        ('u', 'Unavailable')
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='u',
        help_text='Book availability',
    )

    class Meta:
        permissions = (("can_marked_returned", "Set book as returned"),
                       ("can_add_edit", "Can add/edit book instances"),)

    def __str__(self):
        """String representing the model object"""
        return f'{self.id} ({self.book.title})'

    def get_status(self):
        return self.status


class Author(models.Model):
    """Model representing an Author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_add", "Can add authors"),
                       ("can_edit", "Can edit authors"),
                       ("can_delete", "Can delete authors"))

    def get_absolute_url(self):
        """Returns the url to access a particulat author instance"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String representation for the Model object"""
        return f'{self.last_name}, {self.first_name}'
