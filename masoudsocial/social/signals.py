from django.db.models.signals import m2m_changed,post_delete,post_save,pre_delete
from django.contrib.auth.signals import user_logged_in,user_logged_out
from django.dispatch import receiver 
from .models import Post,User,Comment,Activity,Contact
from django.core.mail import send_mail 


@receiver(m2m_changed,sender=Post.likes.through,) 
def user_likes_changed(sender,instance,**kwargs):
    instance.total_likes=instance.likes.count()
    instance.save()


@receiver(m2m_changed,sender=Post.saved_by.through,) 
def user_saved_changed(sender,instance,**kwargs):
    instance.total_saved=instance.saved_by.count()
    instance.save()


@receiver(post_delete, sender=Post)
def delete_post_email(sender, instance, **kwargs):
    author = instance.author
    subject = "Your post has been deleted"
    message = f"Your post with the following description has been deleted:\n{instance.description}"
    send_mail(subject, message, 'fatigram.send@gmail.com', [author.email],
              fail_silently=False)
    

@receiver(post_save,sender=User,) 
def default_job_after_registrations(sender,instance,**kwargs):
    if not instance.job:
        instance.job="بیکار"
        instance.save()


@receiver(post_save, sender=Comment)
def create_activity_on_comment(sender, instance, created, **kwargs):
    if created:
        user = instance.writer
        activity = Activity(user=user, activity_type=f"کامنت روی پستی با این کپشن:\n{instance.post.description}")
        activity.save()


@receiver(m2m_changed, sender=Post.likes.through)
def create_activity_on_like(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            activity = Activity(user=user, activity_type=f"لایک پستی با این کپشن:\n{instance.description}")
            activity.save()
    elif action == 'post_remove':
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            activity = Activity(user=user, activity_type=f"آنلایک پستی با این کپشن:\n{instance.description}")
            activity.save()


@receiver(post_save, sender=Contact)
def create_follow_activity(sender, instance, created, **kwargs):
    if created:
        user = instance.user_from
        activity = Activity.objects.create(user=user, activity_type=f'فالو کردن {instance.user_to.username}')

@receiver(post_delete, sender=Contact)
def create_unfollow_activity(sender, instance, **kwargs):
    user = instance.user_from
    activity = Activity.objects.create(user=user, activity_type=f'آنفالو کردن {instance.user_to.username}')



@receiver(user_logged_in)
def create_login_activity(sender, user, **kwargs):
    activity = Activity(user=user, activity_type="ورود به حساب کاربری")
    activity.save()


@receiver(user_logged_out)
def create_logout_activity(sender, user, **kwargs):
    activity = Activity(user=user, activity_type="خروج از حساب کاربری")
    activity.save()


# @receiver(post_save,sender=User,) 
# def default_photo_after_registrations(sender,instance,**kwargs):
#     if not instance.photo:
#         instance.photo=r"C:\Users\masoud\Desktop\djangoProject\masoudSocial\masoudsocial\media\Avatar.png"
#         instance.save()


# @receiver(pre_delete,sender=User,) 
# def default_photo_after_deleting_photo(sender,instance,**kwargs):
#     if not instance.photo:
#         instance.photo=r"C:\Users\masoud\Desktop\djangoProject\masoudSocial\masoudsocial\media\Avatar.png"
#         instance.save()