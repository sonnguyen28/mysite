from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

<<<<<<< HEAD
admin.site.register(Genre)
admin.site.register(Language)

@admin.register(Author)
=======
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)

# Define the admin class


>>>>>>> cfd55c3 (Django Tutorial Part 4: Django admin site)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')

    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

<<<<<<< HEAD
=======

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

# Register the Admin classes for Book using the decorator

>>>>>>> cfd55c3 (Django Tutorial Part 4: Django admin site)
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')

    inlines = [BooksInstanceInline]

<<<<<<< HEAD
=======
# Register the Admin classes for BookInstance using the decorator


>>>>>>> cfd55c3 (Django Tutorial Part 4: Django admin site)
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )
