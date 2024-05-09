from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User,auth
from django.http import HttpResponse
from social.models import Profile,Post,LikePost,Followers
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from itertools import chain
import random

# Create your views here.


def userreg(request):
    if request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,"email taken")
                return redirect(userreg)
            elif User.objects.filter(username=username).exists():
                messages.info(request,"Username already Taken")
                return redirect(userreg)
            else:
                user=User.objects.create_user(username=username,email=email,password=password)
                user.save()

                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                messages.success(request,"Registration successfull...!")
                return redirect(userlogin)
        else:
            messages.error(request,"Password not matching..!")
            return redirect(userreg)
    return render(request,"registerpage.html")



def userlogin(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect(home)
        else:
            messages.error(request,"Invalid Username or Password")
            return redirect(userlogin)
    else:
        return render(request,"loginpage.html")

@login_required(login_url='/userlogin')
def logoutuser(request):
    auth.logout(request)
    return redirect(userlogin)

@login_required(login_url='/userlogin')
def home(request):
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)

    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')

    profile = Profile.objects.get(user=request.user)

    # user suggestion starts here

    all_users = User.objects.all()
    user_following_all = []

    for user in following_users:
        user_list = User.objects.get(username=user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    # user suggestion ends

    context = {
        'post': post,
        'profile': profile,
        'suggestions_username_profile_list':suggestions_username_profile_list,
    }
    return render(request, 'main.html', context)



@login_required(login_url='/userlogin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect(home)
    else:
        return redirect(home)



@login_required(login_url='/userlogin')
def likes(request,id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)

        like_filter = LikePost.objects.filter(post_id=id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save()

        # Generate the URL for the current post's detail page
        print(post.id)

        # Redirect back to the post's detail page
        return redirect('/social/#'+id)

@login_required(login_url='/userlogin')
def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile

    }
    return render(request, 'explore.html', context)



@login_required(login_url='/userlogin')
def profile(request, id_user):
    user_object = User.objects.get(username=id_user)
    print(user_object)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')
    user_post_length = len(user_posts)

    follower = request.user.username
    user = id_user

    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    user_followers = len(Followers.objects.filter(user=id_user))
    user_following = len(Followers.objects.filter(follower=id_user))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()

            return redirect('/social/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)

    return render(request, 'profile.html', context)


@login_required(login_url='/userlogin')
def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()

    return redirect('/social/profile/'+ request.user.username)




@login_required(login_url='/userlogin')
def search_results(request):
    query = request.GET.get('q')

    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)
    profile = Profile.objects.get(user=request.user)
    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'profile':profile
    }
    return render(request, 'search_user.html', context)




def home_post(request,id):
    post=Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context={
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html',context)



def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/social/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/social/profile/'+user)
    else:
        return redirect('/')



def view_post(request,id):
    post=Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context={
        'post':post,
        'profile':profile
    }
    return render(request,"view_posts.html",context)










