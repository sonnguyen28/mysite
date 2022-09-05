from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author/search/', views.AuthorSearch.as_view(), name='author-search'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),

    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),
    path('borrow-search/', views.BookInstanceSearch.as_view(), name='borrow-search'),

    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),

    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('book/search/', views.BookSearch.as_view(), name='book-search'),
    path('book/<uuid:pk>/borrow/', views.BookBorrow, name='book-borrow'),
    path('book/<uuid:pk>/return/', views.BookReturn, name='book-return'),
    path('book/<uuid:pk>/request/', views.change_borrow_request, name='changes-borrow-status'),
]
