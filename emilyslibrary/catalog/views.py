from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Review


def index(request):
    """View function for the home page of site"""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books
    num_instances_avail = BookInstance.objects.filter(
        status__exact='a').count()

    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_avail': num_instances_avail,
        'num_authors': num_authors,
    }

    return render(request, 'index.html', context=context)
