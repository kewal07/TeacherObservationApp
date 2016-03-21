from django.db import models
from datetime import date
from django.conf import settings
from django.template.defaultfilters import slugify
import hashlib, hmac, os

# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "profilepic%s.%s" % (instance.user_pk, ext)
	# profilePath = (os.path.join(settings.BASE_DIR,'media/profile/'))
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'profile'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

class ExtendedUser(models.Model):
	tdate = date.today()
	def_bday = tdate.replace(year = tdate.year - 16)
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	user_pk = models.CharField(max_length=255)
	imageUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	birthDay = models.DateField(default=def_bday)
	gender = models.CharField(max_length=1,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	bio = models.CharField(max_length=1024,blank=True,null=True)
	profession = models.CharField(max_length=512,blank=True,null=True)
	user_slug = models.SlugField(null=True,blank=True)

	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		uname = self.user.username
		# uname = ''.join(e for e in uname if e.isalnum())
		uslug = slugify(uname)
		if not uslug and not uslug.strip():
			uslug = None
		self.user_slug = uslug
		digestmod = hashlib.sha1
		msg = self.user.email.encode('utf-8')
		key = self.user.username.encode('utf-8')
		sig = hmac.HMAC(key, msg, digestmod).hexdigest()
		self.user_pk = sig
		super(ExtendedUser, self).save(*args, **kwargs)
		"""
		if self.imageUrl:
			size = 128, 128
			im = Image.open(self.imageUrl)
			im.thumbnail(size)
			im.save(self.imageUrl.path)
		"""

	def get_profile_pic_name(self):
		return self.imageUrl.path.split(os.sep)[-1]

	def get_full_name(self):
		return self.user.first_name+ " "+self.user.last_name

	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.imageUrl.path.split(os.sep)[-2]
			# print(day.split("-"))
			# print(day,int(day.split("-")[0]),int(day.split("-")[2]),int(day.split("-")[3]))
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day

	def get_profile_pic_url(self):
		default_pic_url = "/static/login/images/defaultAvatar.png"
		# if self.user.socialaccount_set.all():
		if self.imageUrl:
			img_url = self.imageUrl.path
			#print(img_url)
			# img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
			# print(img_url)
			if img_url.find("https:/") != -1:
				img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
				return r"https://"+self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/https:/","")
			elif img_url.find("http:/") != -1:
				img_url = self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/","")
				return r"http://"+self.imageUrl.path.replace("/home/ubuntu/askpopulo/media/http:/","")
			else:
				# print("/media/profile/"+self.get_profile_pic_name())
				return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		# else:
		# 	if self.imageUrl:
		# 		return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		return default_pic_url

	def calculate_age(self):
		try:
			today = date.today()
			born = self.birthDay
			try:
				birthday = born.replace(year=today.year)
			except ValueError: # raised when birth date is February 29 and the current year is not a leap year
				birthday = born.replace(year=today.year, month=born.month+1, day=1)
			if birthday > today:
				# print(today.year - born.year - 1)
				return today.year - born.year - 1
			else:
				# print(today.year - born.year)
				return today.year - born.year
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
