from django.db import models
from django.conf import settings
import os

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "book%s.%s" % (instance.isbn, ext)
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'books'+os.sep))
	return os.path.join(profilePath,filename)

def get_file_path_coverimages(instance, filename):
	ext = filename.split('.')[-1]
	filename = "bookcoverimage%s.%s" % (instance.isbn, ext)
	coverimage = (os.path.join(settings.BASE_DIR,'media'+os.sep+'coverimage'+os.sep))
	return os.path.join(coverimage,filename)

class Book(models.Model):
	author = models.CharField(max_length=255)
	isbn = models.CharField(max_length=255)
	bookName = models.CharField(max_length=255)
	bookEpub = models.FileField(upload_to=get_file_path,blank=True,null=True)
	coverImageUrl = models.ImageField(upload_to=get_file_path_coverimages,blank=True,null=True)
	pub_date = models.DateTimeField('Date Published')

	def __str__(self):
		return self.bookName

	def has_image(self):
		image_list = []
		if self.featured_image:
			image_list.append("/media/coverimage/"+self.get_file_name())
		return image_list

	def get_file_name(self):
		return self.coverImageUrl.path.split(os.sep)[-1]

	def get_cover_image_path(self):
		return "/media/coverimage/"+self.get_file_name()

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

class BooksIssued(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    book = models.ForeignKey(Book)
