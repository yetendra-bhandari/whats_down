from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('content/', views.content, name='content'),
    path('content/<int:p_id>/', views.viewPost, name='viewPost'),
    path('latest/', views.latest, name='latest'),
    path('latest/<int:page>/', views.latest, name='latestPage'),
    path('trending/', views.trending, name='trending'),
    path('trending/<int:page>/', views.trending, name='trendingPage'),
    path('create/', views.create, name='create'),
    path('confirmPost/', views.confirmPost, name='confirmPost'),
    path('createPost/', views.createPost, name='createPost'),
    path('edit/<int:p_id>/', views.edit, name='edit'),
    path('editPost/', views.editPost, name='editPost'),
    path('deletePost/', views.deletePost, name='deletePost'),
    path('star/<int:p_id>/', views.star, name='star'),
    path('comment/<int:p_id>/', views.comment, name='comment'),
    path('deleteComment/', views.deleteComment, name='deleteComment'),
    path('vote/<int:c_id>/', views.vote, name='vote'),
    path('profile/', views.profile, name='profile'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('profile/<username>/', views.viewProfile, name='viewProfile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about')
]
