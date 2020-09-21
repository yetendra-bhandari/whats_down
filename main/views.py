from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from .lib import saltedHash, toMarkdown, validName, validEmail
from .models import Account, Post, Comment
import math
LIMIT = 5


def index(request):
    if('user_id' in request.session):
        return redirect('main:content')
    message = None
    login_username = None
    if('login_username' in request.session):
        login_username = request.session['login_username']
        request.session.pop('login_username')
    if('message' in request.session):
        message = request.session['message']
        request.session.pop('message')
    return render(request, 'main/index.html', context={'message': message, 'login_username': login_username})


def content(request):
    username = None
    message = None
    latest_posts = Post.objects.order_by('-id')[:5]
    most_starred = Post.objects.order_by('-stars', '-id')[:5]
    your_posts = None
    if('username' in request.session):
        user_id = request.session['user_id']
        username = request.session['username']
        your_posts = Post.objects.filter(owner__id=user_id).order_by('-id')[:5]
    if('message' in request.session):
        message = request.session['message']
        request.session.pop('message')
    return render(request, 'main/content.html', context={'username': username, 'message': message, 'latest_posts': latest_posts, 'most_starred': most_starred, 'your_posts': your_posts})


def viewPost(request, p_id):
    try:
        post = Post.objects.get(Q(id=p_id))
    except(Post.DoesNotExist):
        request.session['message'] = 'Post not available'
        return redirect('main:content')
    account = None
    message = None
    if('user_id' in request.session):
        account = Account.objects.get(id=request.session['user_id'])
    if('message' in request.session):
        message = request.session['message']
        request.session.pop('message')
    comments = Comment.objects.filter(post__id=p_id).order_by('id')
    post.body = toMarkdown(post.body)
    for comment in comments:
        comment.body = toMarkdown(comment.body)
    return render(request, 'main/viewPost.html', context={'account': account, 'message': message, 'post': post, 'comments': comments})


def latest(request, page=1):
    count = Post.objects.count()
    pages = math.ceil(count/LIMIT)
    username = None
    start = (page-1)*LIMIT
    latest_posts = Post.objects.order_by('-id')[start:start+LIMIT]
    if('username' in request.session):
        username = request.session['username']
    return render(request, 'main/latest.html', context={'username': username, 'latest_posts': latest_posts, 'curr_page': page, 'pages': range(pages)})


def trending(request, page=1):
    count = Post.objects.count()
    pages = math.ceil(count/LIMIT)
    username = None
    start = (page-1)*LIMIT
    trending_posts = Post.objects.order_by('-stars', '-id')[start:start+LIMIT]
    if('username' in request.session):
        username = request.session['username']
    return render(request, 'main/trending.html', context={'username': username, 'trending_posts': trending_posts, 'curr_page': page, 'pages': range(pages)})


def create(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must login in order to create posts'
        return redirect('main:index')
    post_fields = {'heading': None, 'body': None}
    if('post_fields' in request.session):
        post_fields = request.session['post_fields']
    return render(request, 'main/create.html', context={'username': request.session['username'], 'post_fields': post_fields})


def confirmPost(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must login in order to create posts'
        return redirect('main:index')
    if(request.method == 'POST' and request.POST.keys() >= {'heading', 'body'}):
        HEAD = request.POST['heading']
        BODY = request.POST['body']
        post_fields = {'error': [], 'heading': HEAD, 'body': BODY}
        if(len(HEAD) == 0):
            post_fields['error'].append(
                'Please enter a title for your post')
        if(len(HEAD) > 128):
            post_fields['error'].append(
                'Heading cannot be of more than 128 characters')
        if(len(BODY) > 4096):
            post_fields['error'].append(
                'Description too long, consider adding extra information in a comment')
        request.session['post_fields'] = post_fields
        return redirect('main:confirmPost')
    if('post_fields' in request.session and not request.session['post_fields']['error']):
        confirm_fields = request.session['post_fields']
        confirm_fields['body'] = toMarkdown(confirm_fields['body'])
        return render(request, 'main/confirm.html', context={'username': request.session['username'], 'confirm_fields': confirm_fields})
    return redirect('main:create')


def createPost(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to create posts'
        return redirect('main:index')
    if('post_fields' in request.session and not request.session['post_fields']['error']):
        account = Account.objects.get(Q(id=request.session['user_id']))
        HEAD = request.session['post_fields']['heading'].strip()
        BODY = request.session['post_fields']['body'].strip()
        post = Post.objects.create(
            owner=account, heading=HEAD, body=BODY)
        request.session['message'] = 'Posted successfully'
        request.session.pop('post_fields')
        return redirect('main:viewPost', post.id)
    return redirect('main:create')


def edit(request, p_id):
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to edit posts'
        return redirect('main:index')
    try:
        username = request.session['username']
        post = Post.objects.get(Q(id=p_id))
        if(post.owner.id == request.session['user_id']):
            editPost_errors = []
            if('editPost_errors' in request.session):
                editPost_errors = request.session['editPost_errors']
                request.session.pop('editPost_errors')
            return render(request, 'main/editPost.html', context={'username': username, 'editPost_errors': editPost_errors, 'post': post})
        request.session['message'] = 'You can only edit your own posts'
    except(Post.DoesNotExist):
        request.session['message'] = 'Post not available'
    return redirect('main:content')


def editPost(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to edit posts'
        return redirect('main:index')
    if(request.method == 'POST' and request.POST.keys() >= {'p_id', 'heading', 'body'}):
        try:
            ID = request.session['user_id']
            PAGE = request.POST['p_id']
            HEAD = request.POST['heading']
            BODY = request.POST['body']
            post = Post.objects.get(Q(id=PAGE))
            if(post.owner.id == ID):
                editPost_errors = []
                valid = True
                if(len(HEAD) == 0):
                    editPost_errors.append(
                        'Please enter a title for your post')
                    valid = False
                if(len(HEAD) > 128):
                    editPost_errors.append(
                        'Heading cannot be of more than 128 characters')
                    valid = False
                if(len(BODY) > 4096):
                    editPost_errors.append(
                        'Description too long, consider adding extra information in a comment')
                    valid = False
                if(valid):
                    post.heading = HEAD
                    post.body = BODY
                    post.save()
                    request.session['message'] = 'Post edited successfully'
                    return redirect('main:viewPost', post.id)
                else:
                    request.session['editPost_errors'] = editPost_errors
                    redirect('main:editPost', post.id)
            else:
                request.session['message'] = 'You can only edit your own posts'
        except(Post.DoesNotExist):
            request.session['message'] = 'Post not available'
    return redirect('main:content')


def deletePost(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to delete posts'
        return redirect('main:index')
    if(request.method == 'POST' and 'p_id' in request.POST):
        try:
            ID = request.session['user_id']
            PAGE = request.POST['p_id']
            post = Post.objects.get(Q(id=PAGE))
            if(post.owner.id == ID):
                post.delete()
                request.session['message'] = 'Post deleted successfully'
            else:
                request.session['message'] = 'You can only delete your own posts'
        except(Post.DoesNotExist):
            request.session['message'] = 'Post not available'
    return redirect('main:content')


def star(request, p_id):
    if('user_id' not in request.session):
        request.session['message'] = 'You must login to star posts'
        return redirect('main:index')
    try:
        if(request.method == 'POST' and 'star' in request.POST):
            post = Post.objects.get(Q(id=p_id))
            account = Account.objects.get(Q(id=request.session['user_id']))
            star = Post.objects.filter(
                Q(id=p_id) & Q(starred_by__id=account.id))
            if(request.POST['star'] == 'false' and star.exists()):
                post.starred_by.remove(account)
                post.stars -= 1
                post.save()
            elif(request.POST['star'] == 'true' and not star.exists()):
                post.starred_by.add(account)
                post.stars += 1
                post.save()
            return redirect('main:viewPost', post.id)
    except(Post.DoesNotExist):
        request.session['message'] = 'Post not available'
        return redirect('main:content')


def comment(request, p_id):
    try:
        comment_post = Post.objects.get(Q(id=p_id))
    except(Post.DoesNotExist):
        request.session['message'] = 'Post not available'
        return redirect('main:content')
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to comment'
        return redirect('main:index')
    if(request.method == "POST" and 'body' in request.POST):
        BODY = request.POST['body'].strip()
        if(len(BODY) > 4096):
            request.session['message'] = 'Comment too long. Consider using multiple comments'
            return redirect('main:content')
        ID = request.session['user_id']
        account = Account.objects.get(Q(id=ID))
        _ = Comment.objects.create(owner=account, post=comment_post, body=BODY)
    return redirect('main:viewPost', p_id)


def deleteComment(request):
    if('user_id' not in request.session):
        request.session['message'] = 'You must log in to delete comments'
        return redirect('main:index')
    if(request.method == 'POST' and 'c_id' in request.POST):
        try:
            ID = request.session['user_id']
            COMM = request.POST['c_id']
            comment = Comment.objects.get(Q(id=COMM))
            if(comment.owner.id == ID):
                comment.delete()
                request.session['message'] = 'Comment deleted successfully'
                return redirect('main:viewPost', comment.post.id)
            else:
                request.session['message'] = 'You can only delete your own comments'
        except(Comment.DoesNotExist):
            request.session['message'] = 'Comment not available'
    return redirect('main:content')


def vote(request, c_id):
    if('user_id' not in request.session):
        request.session['message'] = 'You must login to upvote/downvote comments'
        return redirect('main:index')
    try:
        if(request.method == 'POST' and 'vote' in request.POST):
            comment = Comment.objects.get(Q(id=c_id))
            account = Account.objects.get(Q(id=request.session['user_id']))
            vote = Comment.objects.filter(
                Q(id=c_id) & Q(voted_by__id=account.id))
            if(request.POST['vote'] == 'false' and vote.exists()):
                comment.voted_by.remove(account)
                comment.votes -= 1
                comment.save()
            elif(request.POST['vote'] == 'true' and not vote.exists()):
                comment.voted_by.add(account)
                comment.votes += 1
                comment.save()
            return redirect('main:viewPost', comment.post.id)
    except(Comment.DoesNotExist):
        request.session['message'] = 'Comment not available'
        return redirect('main:content')


def profile(request):
    if('user_id' in request.session):
        editProfile_errors = []
        if('editProfile_errors' in request.session):
            editProfile_errors = request.session['editProfile_errors']
            request.session.pop('editProfile_errors')
        account = Account.objects.defer('password').get(
            Q(id=request.session['user_id']))
        return render(request, 'main/editProfile.html', context={'account': account, 'editProfile_errors': editProfile_errors})
    request.session['message'] = 'You need to login to edit your profile'
    return redirect('main:index')


def editProfile(request):
    if('user_id' in request.session):
        editProfile_errors = []
        if(request.method == 'POST' and request.POST.keys() >= {'name', 'tagline', 'dob', 'new_password', 'new_confirm', 'curr_password'}):
            valid = True
            NAME = request.POST['name'].strip()
            TAGLINE = request.POST['tagline'].strip()
            DOB = request.POST['dob']
            NEW = request.POST['new_password']
            CONF = request.POST['new_confirm']
            CURR = request.POST['curr_password']
            if(len(NAME) > 64):
                editProfile_errors.append(
                    'Name can be of atmost 64 characters')
                valid = False
            if(not validName(NAME)):
                editProfile_errors.append(
                    'Name can only consist of letters')
                valid = False
            if(len(TAGLINE) > 128):
                editProfile_errors.append(
                    'Tagline can be of atmost 128 characters')
                valid = False
            if(NEW and CONF):
                if(len(NEW) < 8 or len(NEW) > 32):
                    editProfile_errors.append(
                        'Password should be of 8-32 characters')
                    valid = False
                if(NEW != CONF):
                    editProfile_errors.append(
                        'Passwords do not match')
                    valid = False
            if(valid):
                try:
                    account = Account.objects.defer('password').get(
                        Q(id=request.session['user_id']) & Q(password=saltedHash(CURR)))
                    account.name = NAME
                    if(TAGLINE):
                        account.tagline = TAGLINE
                    account.date_of_birth = DOB
                    if(NEW and CONF):
                        account.password = saltedHash(NEW)
                    try:
                        account.save()
                        request.session['message'] = 'Changes saved successfully'
                        return redirect('main:content')
                    except(ValidationError):
                        editProfile_errors.append('Invalid date format')
                except(Account.DoesNotExist):
                    editProfile_errors.append('Wrong password')
        else:
            editProfile_errors.append('Enter your details here')
        request.session['editProfile_errors'] = editProfile_errors
        return redirect('main:profile')
    request.session['message'] = 'You need to login to edit your profile'
    return redirect('main:index')


def viewProfile(request, username):
    user = None
    if('username' in request.session):
        user = request.session['username']
    try:
        account = Account.objects.defer('password').get(Q(username=username))
        posts = Post.objects.filter(owner__id=account.id).order_by('-id')
        return render(request, 'main/viewProfile.html', context={'username': user, 'account': account, 'posts': posts})
    except(Account.DoesNotExist):
        request.session['message'] = 'Username does not exist'
        return redirect('main:index')


def login(request):
    request.session.flush()
    message = None
    login_username = None
    valid = True
    if(request.method == 'POST'):
        if(request.POST.keys() >= {'username', 'password'} and len(request.POST['username']) > 0 and len(request.POST['password']) > 0):
            USER = request.POST['username'].strip().lower()
            HASH = saltedHash(request.POST['password'])
            try:
                account = Account.objects.only('username').get(
                    (Q(username=USER) | Q(email=USER)) & Q(password=HASH))
            except(Account.DoesNotExist):
                message = 'Username with the specified password does not exist'
                login_username = USER
                valid = False
        else:
            message = 'Please fill both fields'
            valid = False
    else:
        message = 'Enter your details here'
        valid = False
    if(valid):
        request.session['user_id'] = account.id
        request.session['username'] = account.username
        request.session['message'] = 'Logged in successfully'
        if('remember' in request.POST and request.POST['remember']):
            request.session.set_expiry(604800)
    else:
        request.session['message'] = message
        request.session['login_username'] = login_username
    return redirect('main:index')


def logout(request):
    request.session.flush()
    request.session['message'] = 'Logged out successfully'
    return redirect('main:index')


def signup(request):
    signup_fields = {'error': [], 'name': None,
                     'email': None, 'username': None, 'tagline': None, 'dob': None}
    if('user_id' in request.session):
        request.session.flush()
    if('signup_fields' in request.session):
        signup_fields = request.session['signup_fields']
        request.session.pop('signup_fields')
    return render(request, 'main/signup.html', context={'signup_fields': signup_fields})


def register(request):
    request.session.flush()
    signup_fields = {'error': [], 'name': None,
                     'email': None, 'username': None, 'tagline': None, 'dob': None}
    valid = True
    redirect_page = 'main:signup'
    if(request.method == 'POST'):
        if(request.POST.keys() >= {'name', 'email', 'username', 'tagline', 'dob', 'password', 'confirm'}
           and len(request.POST['name']) > 0 and len(request.POST['email']) > 0 and len(request.POST['username']) > 0 and len(request.POST['password']) > 0 and len(request.POST['confirm']) > 0):
            NAME = signup_fields['name'] = request.POST['name'].strip()
            EMAIL = signup_fields['email'] = request.POST['email'].strip().lower(
            )
            USER = signup_fields['username'] = request.POST['username'].strip(
            ).lower()
            TAGLINE = signup_fields['tagline'] = request.POST['tagline'].strip(
            )
            DOB = signup_fields['dob'] = request.POST['dob']
            PASS = request.POST['password']
            CONF = request.POST['confirm']
            if(len(NAME) > 64):
                signup_fields['error'].append(
                    'Name can be of atmost 64 characters')
                valid = False
            if(not validName(NAME)):
                signup_fields['error'].append(
                    'Name can only consist of letters')
                valid = False
            if(len(EMAIL) > 64):
                signup_fields['error'].append(
                    'Email can be of atmost 64 characters')
                valid = False
            if(not validEmail(EMAIL)):
                signup_fields['error'].append(
                    'Please enter a valid email-address')
                valid = False
            if(Account.objects.filter(Q(email=EMAIL)).exists()):
                signup_fields['error'].append(
                    'An account with the given email-address already exists')
                valid = False
            if(len(USER) > 32):
                signup_fields['error'].append(
                    'Username can be of atmost 32 characters')
                valid = False
            if(not USER.isalnum()):
                signup_fields['error'].append(
                    'Username should only consist of letters and numbers')
                valid = False
            if(Account.objects.filter(Q(username=USER)).exists()):
                signup_fields['error'].append(
                    'Username already taken')
                valid = False
            if(len(TAGLINE) > 128):
                signup_fields['error'].append(
                    'Tagline can be of atmost 128 characters')
                valid = False
            if(len(PASS) < 8 or len(PASS) > 32):
                signup_fields['error'].append(
                    'Password should be of 8-32 characters')
                valid = False
            if(PASS != CONF):
                signup_fields['error'].append(
                    'Passwords do not match')
                valid = False
        else:
            signup_fields['error'].append(
                'Please fill all the required fields')
            valid = False
    else:
        signup_fields['error'].append('Enter your details here')
        valid = False
    if(valid):
        HASH = saltedHash(PASS)
        try:
            account = Account.objects.create(username=USER, name=NAME, email=EMAIL,
                                             password=HASH, tagline=TAGLINE,  date_of_birth=DOB)
            request.session['user_id'] = account.id
            request.session['username'] = account.username
            request.session['message'] = 'Registration successful'
            if('remember' in request.POST and request.POST['remember']):
                request.session.set_expiry(604800)
            redirect_page = 'main:content'
        except(ValidationError):
            signup_fields['error'].append('Invalid date format')
    else:
        request.session['signup_fields'] = signup_fields
    return redirect(redirect_page)


def about(request):
    username = None
    if('username' in request.session):
        username = request.session['username']
    return render(request, 'main/about.html', context={'username': username})
