from cProfile import Profile
import json
from itertools import chain
from multiprocessing import context

import profile
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .models import User, Post, Comment, Following, UserProfile, Like
from .forms import CreatePostForm, CreateCommentForm, CreatePostForm1, CreateUserProfileForm

#TODO: custom 404 page

def index(request):
    """ View: Show all posts """

    # Get all posts
    all_posts = Post.objects.order_by("-date").all()    

    # Create page controll
    p = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    if not request.user.is_authenticated:
        return render(request, "network/index.html", {
        "post_form": CreatePostForm(),
        "comment_form": CreateCommentForm(auto_id=False),
        "page_obj": page_obj,
        "add_post_available": True,
        
        })
    else:
        profile = UserProfile.objects.get(user=request.user)    
        return render(request, "network/index.html", {
        "post_form": CreatePostForm(),
        "comment_form": CreateCommentForm(auto_id=False),
        "page_obj": page_obj,
        "add_post_available": True,
        "profile" : profile,
        })
    
@login_required
def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = UserProfile.objects.get(user=user)
        like= Like.objects.create(user=profile, post_id=post_id)
    
        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
            like.value='Unlike'
        
        else:
            post_obj.liked.add(profile)
            like.value='Like'

        post_obj.save()
        like.save()
        
        return HttpResponseRedirect(reverse(
                    "index",
                ))
@login_required(login_url="network:login")
def category(request, cat):
    category_post=Post.objects.filter(categ=cat).order_by("-date")
   # posts = category_post.posts.order_by("-date")
    profile = UserProfile.objects.get(user=request.user) 
    return render(request, 'network/category.html', {
        'cat': cat,
        'page_obj':category_post,
        'add_post_available': True,
        "post_form": CreatePostForm(),
        "comment_form": CreateCommentForm(auto_id=False),
        "profile":profile
        
        })

    
       

@login_required(login_url="network:login")
def post_comment(request, action):
    """ View: Controls saving a new post/comment (only POST) """

    # Get not allowed
    if request.method == "GET":
        return HttpResponse(status=405)

    if request.method == "POST":
        if action == "post":
            form = CreatePostForm(request.POST)

            if form.is_valid():
                # Get all data from the form
                content = form.cleaned_data["content"]
                categ = form.cleaned_data["categ"]

                # Save the record
                post = Post(
                    user = User.objects.get(pk=request.user.id),
                    content = content,
                    categ= categ
                )
                post.save()
        elif action == "comment":
            form = CreateCommentForm(request.POST)

            if form.is_valid():
                # Get all data from the form
                content = form.cleaned_data["content"]

                # Get commented post
                try:
                    post = Post.objects.get(pk=request.POST.get('postId'))
                except Post.DoesNotExist:
                    return HttpResponse(status=404)

                # Save the record
                comment = Comment(
                    user = User.objects.get(pk=request.user.id),
                    content = content,
                    post = post
                )
                comment.save()
        
        else:
            form = CreatePostForm1(request.POST)

            if form.is_valid():
                # Get all data from the form
                content = form.cleaned_data["content"]
                


                # Save the record
                post = Post(
                    user = User.objects.get(pk=request.user.id),
                    content = content,
                    categ= action
                )
                post.save()
               

        # Go back to the place from which the request came
        return HttpResponseRedirect(request.headers['Referer'])

    
        
       
            
@login_required(login_url="network:login")
def user_profile(request, user_id):
    """ View: Shows requested user profile and the user's posts """

    user_data = User.objects.get(pk=user_id)
    posts = user_data.posts.order_by("-date").all()

    # Get following and followed user objects
    following_id_list = Following.objects.filter(user=user_id).values_list('user_followed', flat=True)
    followers_id_list = Following.objects.filter(user_followed=user_id).values_list('user_id', flat=True)

    following_user_list = User.objects.filter(id__in=following_id_list)
    followers_user_list = User.objects.filter(id__in=followers_id_list)

    # Create page controll
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    profile = UserProfile.objects.get(user=user_data)

    return render(request, "network/user_profile.html", {
        "user_data": user_data,
        "following": following_user_list,
        "followers": followers_user_list,
       "page_obj": page_obj,
        "comment_form": CreateCommentForm(auto_id=False),
        "profile": profile,
    })

@login_required(login_url="network:login")
def edit_profile(request):
    """ View: Controls editing of user profile's data """

    if request.method == "POST":
        
        # Cancel edit -> go back to the profile
        if request.POST.get("cancel") == "clicked":
            return HttpResponseRedirect(reverse(
                    "user-profile",
                    args=[request.user.id]
                ))

        # Submit edit -> update profile
        form = CreateUserProfileForm(request.POST, request.FILES, instance=request.user)
        form.save()
        if form.is_valid():
            # Get current user's profile
            new_profile = UserProfile.objects.get(user=request.user.id)

            # Update all profile's data with form's data
            new_profile.name = form.cleaned_data.get("name")
            new_profile.date_of_birth = form.cleaned_data.get("date_of_birth")
            new_profile.about = form.cleaned_data.get("about")
            new_profile.country = form.cleaned_data.get("country")
            # Update image only if any file was uploaded
            if len(request.FILES) == 1:
                new_profile.image = request.FILES['image']

            # Save changes
            new_profile.save()

            # Go back to user's profile page
            return HttpResponseRedirect(reverse(
                    "user-profile",
                    args=[request.user.id]
                ))
        else:
            # If form invalid - load edit-profile with error info
            return render(request, "network/edit_profile.html", {
                "form": CreateUserProfileForm(instance=request.user.profile),
                #"form": form,
                "max_file_size": settings.MAX_UPLOAD_SIZE
            })

    return render(request, "network/edit_profile.html", {
      "form": CreateUserProfileForm(instance=request.user.profile),
    #    "form": CreateUserProfileForm(),
        "max_file_size": settings.MAX_UPLOAD_SIZE
    })


    
    

@login_required(login_url="network:login")
def following(request):
    """ View: Show users' posts that current user follows"""

    current_user = User.objects.get(pk=request.user.id)

    # Get all posts from users that current user follows
    posts = [users.get_user_followed_posts() for users in current_user.following.all()]

    # Flatten 2d array to 1d array
    posts = list(chain(*posts))

    # Create page controll
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "form": None,
        "comment_form": CreateCommentForm(auto_id=False),
        "page_obj": page_obj,
        "add_post_available": False
    })

@login_required(login_url="network:login")
def follow_unfollow(request, user_id):
    """ View: Controls following/unfollowing users (only POST) """
    # GET method is not allowed
    if request.method == "GET":
        return HttpResponse(status=405)
    # Nested try/except helps to reduce db queries by one
    if request.method == "POST":
        try:
            get_follow_obj = Following.objects.get(user=request.user.id, user_followed=user_id)
        except Following.DoesNotExist:
            try:
                user_to_follow = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return HttpResponse(status=404)
            else:
                new_follow_obj = Following(user=request.user, user_followed=user_to_follow)
                new_follow_obj.save()
        else:
            get_follow_obj.delete()

        return HttpResponseRedirect(reverse("user-profile", args=[user_id]))

def login_view(request):
    """ View: Controls logging in """

    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If user tried to enter login_required page - go there after login
            if "next" in request.POST:
                request_args =  request.POST.get("next")[1:].split('/')
                return HttpResponseRedirect(reverse(
                        "network:" + request_args[0], args=request_args[1:]
                       ))
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": _("Invalid username and/or password.")
            })
    else:
        # Show login panel only for not login users
        if request.user.is_authenticated:
           
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html")


def logout_view(request):
    """ View: Controls logging out """

    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """ View: Controls registration """

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure no blank fields
        if  (not username) or (not email) or (not password):
            return render(request, "network/register.html", {
                "message": _("You must fill out all fields.")
            })
        # Ensure password matches confirmation
        elif password != confirmation:
            return render(request, "network/register.html", {
                "message": _("Passwords must match.")
            })

        # Attempt to create new user and its profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            u_profile = UserProfile()
            u_profile.user=User.objects.get(username=user)
            u_profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": _("Username already taken.")
            })
        login(request, user)
        
        return HttpResponseRedirect(reverse("index"))
    else:
        # Show register panel only for not login users
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/register.html")
        
       