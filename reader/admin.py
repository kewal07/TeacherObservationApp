from django.contrib import admin
from reader.models import BookMark, Note, Highlight, Book, BooksIssued

admin.site.register(Book)
admin.site.register(BookMark)
admin.site.register(Highlight)
admin.site.register(Note)
admin.site.register(BooksIssued)
