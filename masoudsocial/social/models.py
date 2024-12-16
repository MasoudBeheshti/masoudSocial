from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from django.urls import reverse
from django_resized import ResizedImageField

# Create your models here.

class User(AbstractUser):
    # date_of_birth=jmodels.jDateField(verbose_name='تاریخ تولد',blank=True,null=True)   
    date_of_birth=models.DateField(verbose_name='تاریخ تولد',blank=True,null=True)   
    bio=models.TextField(verbose_name='بایو',blank=True,null=True) 
    photo=ResizedImageField(upload_to='account_images/', size=[500, 500], quality=100, crop=['middle', 'center'],blank=True,null=True, verbose_name='تصویر')   
    # photo=models.ImageField(upload_to='account_images/',blank=True,null=True, verbose_name='تصویر')   
    job=models.CharField(max_length=250, verbose_name='شغل', null=True,blank=True)
    phone=models.CharField(max_length=11, verbose_name='شماره تلفن', null=False,blank=False,default='')
    email=models.CharField(max_length=50, verbose_name='ایمیل', null=False,blank=False,default='')
    following = models.ManyToManyField('self', through='Contact', related_name="followers", symmetrical=False)#b shekle self nveshtn dqqt kn. ba through moshakhas mikni table miani chie. related name bar axe following bayad bashe. symmetrical neshun mide rabete motaqaren bashe, yni age yki follow krdet to hm khodkar follow nknish! default e django ine k khodkar follow mikne. 
    insta_id=models.CharField(max_length=30, null=True, blank=True)
    twitter_id=models.CharField(max_length=30, null=True, blank=True)
    facebook_id=models.CharField(max_length=30, null=True, blank=True)


    def get_followers(self):
        return [contact.user_from for contact in self.rel_to_set.all().order_by('-created')]

    def get_following(self):
        return [contact.user_to for contact in self.rel_from_set.all().order_by('-created')]


    def get_absolute_url(self):
        return reverse("social:user_detail", args={self.username})
    

    def delete(self,*args,**kwargs): 
        storage,path= self.photo.storage, self.photo.path
        print(path)
        storage.delete(path)
        super().delete(*args,**kwargs)

class Post(models.Model):
    #relations
    author= models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts",default=1, verbose_name='نویسنده')
    #data fields
    description = models.TextField(verbose_name='توضیحات') 
    tags= TaggableManager(blank=True)
    #date
    created= models.DateTimeField(auto_now_add=True) 
    updated= models.DateTimeField(auto_now=True) 
    likes=models.ManyToManyField(User,related_name='liked_posts',blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    total_likes=models.PositiveIntegerField(default=0)
    total_saves=models.PositiveIntegerField(default=0)
    active=models.BooleanField(default=True)


    # objects=jmodels.jManager()

    class Meta: 
        ordering = ['-created'] 
        indexes= [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes']),
        ]
        verbose_name='پست'
        verbose_name_plural='پست ها'

    def __str__(self): 
        return self.author.first_name
    
    def get_absolute_url(self):
        return reverse("social:post_detail", args={self.id})
    
    def delete(self,*args,**kwargs): 
        for img in self.images.all():
            storage,path= img.image_file.storage, img.image_file.path
            storage.delete(path)
        super().delete(*args,**kwargs)
    


class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments",default=1, verbose_name='پست')
    # name=models.CharField(max_length=250, verbose_name='نام')
    writer=models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments",default=1, verbose_name='نویسنده')
    body=models.TextField(verbose_name='متن کامنت') 
    created= models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد') 

    class Meta: 
        ordering = ['created'] 
        indexes= [
            models.Index(fields=['created'])
        ]
        verbose_name='کامنت'
        verbose_name_plural='کامنت ها'

    def __str__(self): 
        return f"{self.writer.username} : {self.post}"
    


class Image(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images",default=1, verbose_name='پست')
    image_file= ResizedImageField(upload_to='post_image/', size=[500, 500], quality=100, crop=['middle', 'center'])  
    created= models.DateTimeField(auto_now_add=True)   
    title=str(image_file.name).split('/')[-1]
    class Meta: 
        ordering = ['created'] 
        indexes= [
            models.Index(fields=['created'])
        ]
        verbose_name='تصویر'
        verbose_name_plural='تصویر ها'

    def __str__(self): 
        return self.title
    

class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ('-created',)

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
    


class Ticket(models.Model):
    
    message=models.TextField(verbose_name='پیام') 
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tickets",default=1, verbose_name='نویسنده')
    email=models.EmailField(verbose_name='ایمیل')
    phone=models.CharField(max_length=11, verbose_name='شماره تماس')
    subject=models.CharField(verbose_name='موضوع')
    admin_reply=models.TextField(verbose_name='پاسخ ادمین', default='') 
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta: 
        verbose_name='تیکت'
        verbose_name_plural='تیکت ها'

    def __str__(self): 
        return self.subject



class Activity(models.Model):#ye model misazim ba field hayi k lazem dre k save she tu database kara karbar
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_activities",default=1, verbose_name='کاربر')
    activity_type = models.CharField(max_length=250)#noe activity k ba signal por mishe 
    timestamp = models.DateTimeField(auto_now_add=True)#zamane activity


    class Meta:
        indexes = [
            models.Index(fields=['-timestamp'])
        ]
        ordering = ('-timestamp',)


    def __str__(self):
        return f'{self.user.username} - {self.activity_type}'