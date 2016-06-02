from django.db import models
from datetime import date
from django.conf import settings
from django.template.defaultfilters import slugify
import hashlib, hmac, os
# from evaluationapp.models import School

# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "profilepic%s.%s" % (instance.user_pk, ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'profile'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)

class ExternalEvaluator(models.Model):
	external_evaluator_name = models.CharField(max_length=255)
	external_evaluator_designation = models.CharField(max_length=255)
	external_evaluator_organisation = models.CharField(max_length=255)	
	external_evaluator_bio = models.CharField(max_length=1024,blank=True,null=True)
	external_evaluator_picUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	
	def __str__(self):
		return self.external_evaluator_name 

	def get_profile_pic_name(self):
		return self.external_evaluator_picUrl.path.split(os.sep)[-1]

	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.external_evaluator_picUrl.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day

	def get_profile_pic_url(self):
		default_pic_url = "/static/login/images/defaultAvatar.png"
		if self.external_evaluator_picUrl:
			external_evaluator_picUrl = self.external_evaluator_picUrl.path
			if external_evaluator_picUrl.find("https:"+os.sep) != -1:
				return external_evaluator_picUrl.split('media')[1][1:]
			elif external_evaluator_picUrl.find("http:"+os.sep) != -1:
				return external_evaluator_picUrl.split('media')[1][1:]
			else:
				return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		return default_pic_url


class ExtendedUser(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	user_pk = models.CharField(max_length=255)
	imageUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	city = models.CharField(max_length=512,blank=True,null=True)
	state = models.CharField(max_length=512,blank=True,null=True)
	country = models.CharField(max_length=512,blank=True,null=True)
	address = models.CharField(max_length=1024,blank=True,null=True)
	user_slug = models.SlugField(null=True,blank=True)
	is_admin = models.BooleanField(default=0)
	bio = models.CharField(max_length=1024,blank=True,null=True)
	gender = models.CharField(max_length=1,blank=True,null=True)
	# school = models.ForeignKey(School,blank=True,null=True)

	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		uname = self.user.username
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

	def get_profile_pic_name(self):
		return self.imageUrl.path.split(os.sep)[-1]

	def get_full_name(self):
		return self.user.first_name+ " "+self.user.last_name

	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.imageUrl.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day

	def get_profile_pic_url(self):
		default_pic_url = "/static/login/images/defaultAvatar.png"
		if self.imageUrl:
			img_url = self.imageUrl.path
			if img_url.find("https:"+os.sep) != -1:
				return img_url.split('media')[1][1:]
			elif img_url.find("http:"+os.sep) != -1:
				return img_url.split('media')[1][1:]
			else:
				return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		return default_pic_url

