from django.db import models

# Create your models here.

class Book(models.Model):
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    bookname = models.CharField(max_length=255)
    bookepub = models.FileField(upload_to='/media/books',blank=True,null=True)
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
