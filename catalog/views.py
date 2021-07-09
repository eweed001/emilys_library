from django.shortcuts import render, redirect
from .models import Book, Author, BookInstance, Genre, Review
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django import forms
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin


from catalog.models import Author, Review
from catalog.models import Book
from .forms import ReviewForm, RegisterForm


def index(request):
    """View function for the home page of site"""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books
    num_instances_avail = BookInstance.objects.filter(
        status__exact='a').count()

    num_authors = Author.objects.count()

    # number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_avail': num_instances_avail,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['form'] = ReviewForm
        # context['reviews'] = self.object.review_set
        return context


class ReviewFormView(FormView):
    form_class = ReviewForm
    success_url = reverse_lazy('books')
    model = Review
    book_pk = None

    def get_book(self):
        return Review.objects.first().book

    def form_valid(self, form):
        temp = form.cleaned_data.get("book")
        self.book_pk = temp.pk
        item = form.save()
        return super(ReviewFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('book-detail', args=[str(self.book_pk)])


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class ReviewListView(generic.ListView):
    model = Review


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """ Generic class-based view listing books on loan to current user"""
    """Must be logged in to see it (loginrequiredmixin checks this)"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o')


class AllLoanedBooksView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan and the borrowers"""
    permission_required = 'catalog.can_add_edit'
    model = BookInstance
    template_name = 'catalog/all_loaned_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower__isnull=False)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'  # not necessarily best practice


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'isbn', 'description', 'cover_img', 'author', 'genre']


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'isbn', 'description', 'author', 'genre']


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')


def register(response):
    if response.method == 'POST':
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
        return redirect("/accounts/login/")
    else:
        form = RegisterForm()

    return render(response, 'catalog/register.html', {"form": form})
