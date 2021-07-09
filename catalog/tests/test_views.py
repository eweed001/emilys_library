from django.test import TestCase
from django.urls import reverse
from catalog.models import Author

import datetime
from django.utils import timezone
from django.contrib.auth.models import User, Permission

from catalog.models import BookInstance, Book, Genre


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # create 13 authors for pagination test
        num_of_authors = 13

        for author_id in range(num_of_authors):
            Author.objects.create(
                first_name=f'Writer {author_id}',
                last_name=f'Surname {author_id}',)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)


class LoanedBookInstanceByUserListViewTest(TestCase):
    def setUp(self):
        # creating two users
        test_user1 = User.objects.create_user(
            username='test1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='test2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        # create a book
        test_author = Author.objects.create(
            first_name='Mickey', last_name='Mouse')
        test_genre = Genre.objects.create(name='Children')
        test_book = Book.objects.create(
            title='Test Book',
            description='test summary',
            isbn='1234',
            author=test_author,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # creating 30 book instances
        num_of_copies = 30

        for copy in range(num_of_copies):
            borrower = test_user1 if copy % 2 else test_user2
            status = 'u'
            BookInstance.objects.create(
                book=test_book,
                imprint='unlikely imprint',
                borrower=borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='test1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(
            response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(
            username='test1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'test1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')


class AllLoanedBooksViewTest(TestCase):
    def setUp(self):
        # creating two users
        test_user1 = User.objects.create_user(
            username='test1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='test2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        # give user2 permission to view all loaned out books
        permission = Permission.objects.get(name='Can add/edit book instances')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # create a book
        test_author = Author.objects.create(
            first_name='Mickey', last_name='Mouse')
        test_genre = Genre.objects.create(name='Children')
        test_book = Book.objects.create(
            title='Test Book',
            description='test summary',
            isbn='1234',
            author=test_author,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # create a copy loaned to user 1
        BookInstance.objects.create(
            book=test_book,
            imprint='unlikely imprint',
            borrower=test_user1,
            status='o',
        )

        def test_redirect_if_not_loggedin(self):
            response = self.client.get(reverse('all-loaned'))
            self.assertEqual(response.status_code, 302)

        def test_view_all_loaned_when_logged_in(self):
            login = self.client.login(
                username="test2", password="2HJ1vRV0Z&3iD")
            response = self.client.get(reverse('all-loaned'))
            self.assertEqual(response.status_code, 200)
# class RegisterAccountViewTest(TestCase):
