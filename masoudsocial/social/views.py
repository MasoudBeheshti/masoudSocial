from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse,JsonResponse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Post,Image,Contact,Ticket,Activity
from taggit.models import Tag
from django.db.models import Count,Q
from django.contrib.postgres.search import TrigramSimilarity
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib import messages
from django.core.serializers import serialize 

# Create your views here.

def log_out(request):
    logout(request)
    # return render(request,'registration/logged_out.html')
    return redirect(request.META.get('HTTP_REFERER'))
    # return HttpResponse('شما خارج شدید')


@login_required
def profile(request):
    user= User.objects.prefetch_related('followers','following').get(id=request.user.id)
    saved_posts=user.saved_posts.all()
    tickets=user.user_tickets.all()
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')[:10]
    my_posts=user.user_posts.all()[:8]
    following=user.get_following()
    followers=user.get_followers()
    context={
        'saved_posts':saved_posts,
        'tickets':tickets,
        'activities':activities,
        'my_posts':my_posts,
        'following':following,
        'followers':followers,
        'form':CommentForm()
    }
    
    return render(request,'social/profile.html',context)

def register(request):
    if request.method == 'POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # return render(request,'registration/register_done.html',{'user':user})
            return redirect('social:login')
    else:
        form=UserRegistrationForm()
    return render(request,'registration/register.html',{'form':form})


@login_required
def edit_user(request):
    edited=False
    if request.method == 'POST':
        user_form=UserEditForm(request.POST,request.FILES,instance=request.user)
        if user_form.is_valid():
            user_form.save()
            edited=True
        # return redirect('social:profile') 
    else:
        user_form=UserEditForm(instance=request.user)
    context={
        'user_form':user_form,
        'edited':edited
    }
    return render(request,'registration/edit_user.html',context)

@login_required
def ticket(request): 
    if request.method == 'POST':
        form=TicketForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            #for saving tickets in database
            ticket_obj=Ticket.objects.create()
            ticket_obj.message= cd['message']
            ticket_obj.user= request.user
            ticket_obj.email= request.user.email
            ticket_obj.phone= request.user.phone
            ticket_obj.subject= cd['subject']
            ticket_obj.admin_reply= ''
            ticket_obj.save()
            #-----------
            message=f"A user with this username: {ticket_obj.user.username}\nthis email: {ticket_obj.email}\nand this phone number: {ticket_obj.phone}\nsent this ticket: {cd['message']}" 
            send_mail(cd['subject'],message,'fatigram.send@gmail.com',['fatigram.inbox@gmail.com',],fail_silently=False)
            messages.success(request,'ایمیل شما ارسال شد')

    else:
        form=TicketForm()
    return render(request,'forms/ticket.html',{'form':form})

@login_required
def post_list(request, tag_slug=None, username=None):
    posts = Post.objects.select_related('author').order_by('-total_likes')
    latest_users = User.objects.filter(is_active=True).order_by('-date_joined')[:4]
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.select_related('author').filter(tags__in=[tag])

    
    if username is not None:
        userposts=True
        user=User.objects.get(username=username)
        posts = user.user_posts.all()
    else:
        userposts=False

    page = request.GET.get('page')
    paginator = Paginator(posts, 3)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/list_ajax.html', {'posts': posts})
    context = {
        'posts': posts,
        'tag': tag,
        'latest_users': latest_users,
        'userposts': userposts,
    }
    return render(request, "social/list.html", context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form=CreatePostForm(request.POST,request.FILES)
        if form.is_valid():
            post=form.save(commit=False)
            post.author= request.user
            post.save()
            if form.cleaned_data['image1']:
                Image.objects.create(image_file=form.cleaned_data['image1'],post=post)
            if form.cleaned_data['image2']:
                Image.objects.create(image_file=form.cleaned_data['image2'],post=post)
            form.save_m2m()
            return redirect('social:profile')
    else:
        form=CreatePostForm()
    return render(request,'forms/create_post.html',{'form':form})


def post_detail(request,pk):
    post=get_object_or_404(Post,id=pk)
    # form=CommentForm()
    comments=post.comments.all()
    post_tags_ids= post.tags.values_list('id',flat=True)
    similar_posts=Post.objects.select_related('author').filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-created')[:2]
    context={
        'post':post,
        'similar_posts':similar_posts,
        'comments':comments,
        # 'form':form
    }
    return render(request, 'social/detail.html',context)

#for postgresse
def post_search(request):
    query=None
    results=[]
    if 'query' in request.GET:
        form=SearchForm(data=request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            results1=Post.objects.annotate(similarity=TrigramSimilarity('tags__name',query)).filter(similarity__gt=0.1).order_by('-similarity')
            results2=Post.objects.annotate(similarity=TrigramSimilarity('description',query)).filter(similarity__gt=0.1).order_by('-similarity')
            results=(results1|results2).order_by('id','-similarity').distinct('id')
    context={
        'query':query,
        'results':results
    }
    return render(request,'social/search.html',context)


#for mysql
# def post_search(request):
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(data=request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             # You can search in multiple fields using Q objects
#             results = Post.objects.filter(
#                 Q(tags__name__icontains=query) | 
#                 Q(description__icontains=query)
#             ).distinct()  # Use distinct() if you want to avoid duplicates

#     context = {
#         'query': query,
#         'results': results
#     }
    return render(request, 'social/search.html', context)


@require_POST
def post_comment_ajax(request):
    post_id = request.POST.get('post_id') 
    if post_id is not None:
        post=get_object_or_404(Post,id=post_id)
        writer=request.user
        form=CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(post=post,writer=writer)
            comment.body=form.cleaned_data['body']
            comment.save()
            comments_count = post.comments.count()
            # Serialize the comment data
            serialized_comment = serialize('json', [comment], fields=('writer', 'body','created'))
            response_data = {
                'comment': serialized_comment,
                'comments_count':comments_count
            } 
    else:
        response_data = {'error': 'Invalid post_id'}

    return JsonResponse(response_data) 






@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id) 
    images_count = post.images.count()
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.tags.set(form.cleaned_data['tags'])
            post.save()
            if form.cleaned_data['image1']:
                Image.objects.create(image_file=form.cleaned_data['image1'], post=post)
                images_count += 1
            if form.cleaned_data['image2']:
                Image.objects.create(image_file=form.cleaned_data['image2'], post=post)
                images_count += 1
            
            return redirect('social:profile')
    else:
        form = CreatePostForm(instance=post)
    return render(request, 'forms/create_post.html', {'form': form, 'post': post, 'images_count': images_count})


@login_required
def delete_post(request, post_id):
    post=get_object_or_404(Post,id=post_id) 
    if request.method == 'POST': 
        post.delete()
        return redirect('social:profile')
    return render(request,'forms/delete_post.html',{'post':post}) 


@login_required
def delete_image(request, image_id):
    image=get_object_or_404(Image,id=image_id) 
    image.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_profile_image(request):
    image=request.user.photo
    image.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@require_POST 
def like_post(request):
    post_id = request.POST.get('post_id') 
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id) 
        user = request.user 

        if user in post.likes.all():
            post.likes.remove(user) 
            liked = False 
        else:  
            post.likes.add(user)
            liked = True

        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        } 
    else:
        response_data = {'error': 'Invalid post_id'}
    return JsonResponse(response_data) 


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = Post.objects.get(id=post_id)
        user = request.user

        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        post_saved_count = post.total_saves
        return JsonResponse({'saved': saved,'saved_count':post_saved_count})
    return JsonResponse({'error': 'Invalid request'})


@login_required
def user_list(request):
    users = User.objects.prefetch_related('followers','following').filter(is_active=True).order_by('-date_joined') 
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})


@login_required
@require_POST 
def user_follow(request):
    user_id = request.POST.get('id') 
    follower_image_url = request.user.photo.url if request.user.photo else "{% static 'images/profile/Avatar.png' %}"
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            following_image_url = user.photo.url if request.user.photo else "{% static 'images/profile/Avatar.png' %}"
            if request.user in user.followers.all(): 
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user) 
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            current_user_following_count = request.user.following.count()

            return JsonResponse({'follow': follow, 'following_count': following_count,
                                 'followers_count': followers_count,'follower_image_url':follower_image_url,'following_image_url':following_image_url,'current_user_following_count':current_user_following_count})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist.'})

    return JsonResponse({'error': 'Invalid request.'})



@login_required
def user_followers(request,username):
    user = get_object_or_404(User, username=username, is_active=True)
    followers=user.followers.all()
    return render(request, 'user/user_followers.html', {'user': user,'followers':followers})



@login_required
def user_following(request,username):
    user = get_object_or_404(User, username=username, is_active=True)
    following=user.following.all()
    return render(request, 'user/user_following.html', {'user': user,'following':following})




def post_likes(request,pk):
    post=get_object_or_404(Post,id=pk)
    likes=post.likes.all()
    context={
        'likes':likes
    }
    return render(request, 'social/post_likes.html',context)


@require_POST
@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.writer = request.user
        comment.save()
    return redirect(request.META.get('HTTP_REFERER'))



@login_required
def users_tickets(request):
    user=request.user
    tickets=user.user_tickets.all()
    return render(request, 'social/users_tickets.html',{'tickets':tickets})


@login_required
def users_last_activities(request):
    user=request.user
    activities =user.user_activities.order_by('-timestamp')[:10]
    return render(request, 'social/users_last_activities.html',{'activities':activities})


@login_required
def messaging(request):
    return render(request, 'social/messaging.html')


def get_next_image(request):
    id=request.POST.get('post_id')
    post = Post.objects.select_related('author').get(id=id)
    next_image = post.images.all()[1]
    
    return JsonResponse({'image_file_url': next_image.image_file.url})


def get_previous_image(request):
    id=request.POST.get('post_id')
    post = Post.objects.select_related('author').get(id=id)
    previous_image = post.images.all()[0]
    
    return JsonResponse({'image_file_url': previous_image.image_file.url})