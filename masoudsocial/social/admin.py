from django.contrib import admin
from .models import User,Post,Comment,Image,Contact,Ticket,Activity
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail 
# Register your models here.


#inlines
class ImageInline(admin.TabularInline):
    model= Image
    extra=0

class CommentInline(admin.TabularInline):
    model= Comment
    extra=0
    # readonly_fields=['writer','body']



@admin.register(User)
class UserAdmin(UserAdmin):
    list_display=['username','phone','first_name','last_name'] 
    fieldsets= UserAdmin.fieldsets + (('Additional Info',{'fields':('date_of_birth','bio','photo','job','phone')}),)




#actions for postadmin
def make_deactivation(modeladmin, request, queryset):
    reusult = queryset.update(active = False)
    modeladmin.message_user(request, f"{reusult} Posts were rejected" ) 
make_deactivation.short_description ='رد پست'  

def make_activation(modeladmin, request, queryset):
    reusult = queryset.update(active = True)
    modeladmin.message_user(request, f"{reusult} Posts were accepted" )
make_activation.short_description ='تایید پست'

def email_post_status(modeladmin, request, queryset):
    for obj in queryset:
        result = obj.active
        status='rejected'
        if result:
            status='accepted'
        author = obj.author
        subject = "Your post status"
        message = f"Your post with the following content is {status}:\n {obj.description}"
        send_mail(subject, message, 'fatigram.send@gmail.com', [author.email],
                fail_silently=False)
    modeladmin.message_user(request, "Status of post/posts informed to the user/users" )
email_post_status.short_description ='ایمیل وضعیت پست'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin): 
    list_display= ['author','created','description','active']
    ordering= ['created']
    search_fields=['description']
    inlines=[ImageInline,CommentInline]
    actions=[make_deactivation,make_activation,email_post_status]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin): 
    list_display= [ 'post','writer', 'created']
    list_filter=['created']
    search_fields=['body']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin): 
    list_display= [ 'post', 'created']


admin.site.register(Contact)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin): 
    list_display= ['user', 'subject', 'phone','created']


admin.site.register(Activity)
