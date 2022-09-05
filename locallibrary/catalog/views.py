from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
import datetime
from .models import Book, Author, BookInstance, Genre
from turtle import title

from catalog.forms import RenewBookForm, BorrowBookForm, BookRequest


def index(request):
    """View function for home page of site."""

    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['some_data'] = 'This is just some data'
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instance_list'] = self.object.bookinstance_set.all
        return context


class BookSearch(generic.ListView):
    model = Book
    def get_queryset(self):
        query = self.request.GET.get("book")
        book_list = Book.objects.filter(
            Q(title__icontains=query) | Q(genre__name=query) | Q(author__first_name=query) | Q(author__last_name=query)
        ).distinct()
        return book_list


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_book_list'] = Book.objects.all().filter(author=self.object)
        return context


class AuthorSearch(generic.ListView):
    model = Author

    def get_queryset(self):
        query = self.request.GET.get("author")

        if str.isdigit(query) == 1:
            author_list = Author.objects.filter(
                Q(first_name=query) | Q(last_name=query) | Q(date_of_birth__year=query)
            )
            return author_list
        else:
            author_list = Author.objects.filter(
                Q(first_name=query) | Q(last_name=query)
            )
            return author_list


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user, status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'cover_image']
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


@login_required
def BookBorrow(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = BorrowBookForm(request.POST)

        if form.is_valid():
            book_instance.borrow_day = datetime.date.today()
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.borrower = request.user
            book_instance.status = 'o'

            book_instance.save()

            return HttpResponseRedirect(reverse('my-borrowed'))

    else:
        proposed_rent_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = BorrowBookForm(initial={'due_back': proposed_rent_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_borrow.html', context)


@login_required
def BookReturn(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    book_instance.due_back = None
    book_instance.borrower = None
    book_instance.status = 'a'
    book_instance.borrow = 'w'

    book_instance.save()
    return HttpResponseRedirect(reverse('my-borrowed'))


class BookInstanceSearch(generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    def get_queryset(self):
        query = self.request.GET.get("borrow")

        if str.isdigit(query) == 1:
            object_list = BookInstance.objects.filter(
                Q(book__title__icontains=query) | Q(due_back=query)
            )
            print(query)
            return object_list
        else:
            object_list = BookInstance.objects.filter(
                Q(book__title__icontains=query) | Q(borrow=query)
            )
            print(query)
            return object_list


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def change_borrow_request(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = BookRequest(request.POST)

        if form.is_valid():
            book_instance.borrow = form.cleaned_data['borrow']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        form = BookRequest()

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/change_borrow_request.html', context)
