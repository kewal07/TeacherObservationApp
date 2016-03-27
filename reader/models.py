from django.db import models
from django.conf import settings

class Book(models.Model):
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    bookName = models.CharField(max_length=255)
    bookEpub = models.FileField(upload_to='/media/books',blank=True,null=True)
    coverImageUrl = models.ImageField(upload_to='/media/coverimage',blank=True,null=True)
    pub_date = models.DateTimeField('Date Published')

    def __str__(self):
        return self.question_text

    def has_image(self):
        image_list = []
        if self.featured_image:
            image_list.append("/media/coverimages/"+self.get_file_name())
        return image_list

    def get_file_name(self):
        return self.get_folder_day()+"/"+self.featured_image.path.split(os.sep)[-1]

class BookMark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    book = models.ForeignKey(Book)
    bookmarkName = models.CharField(max_length=255)
    chapterHref = models.CharField(max_length=512)
    pageCfi = models.CharField(max_length=512)
    pub_date = models.DateTimeField('Date Published')

    def __str__(self):
        return self.book + "_" + self.user + "_" + self.bookmarkName

class Highlight(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    book = models.ForeignKey(Book)
    text = models.CharField(max_length=4095)
    wordRange = models.CharField(max_length=4095)
    chapterHref = models.CharField(max_length=512)
    pageCfi = models.CharField(max_length=512)
    pub_date = models.DateTimeField('Date Published')

    def __str__(self):
        return self.book + "_" + self.user + "_" + self.text

class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    book = models.ForeignKey(Book)
    text = models.CharField(max_length=4095)
    wordRange = models.CharField(max_length=4095)
    chapterHref = models.CharField(max_length=512)
    pageCfi = models.CharField(max_length=512)
    textCfi = models.CharField(max_length=512)
    pub_date = models.DateTimeField('Date Published')

    def __str__(self):
        return self.book + "_" + self.user + "_" + self.text
