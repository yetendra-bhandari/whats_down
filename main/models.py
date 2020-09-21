from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, unique=True, db_index=True)
    password = models.CharField(
        max_length=64)
    tagline = models.CharField(max_length=128, blank=True)
    date_of_birth = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)+' : '+self.name


class Post(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    heading = models.CharField(max_length=128, db_index=True)
    body = models.TextField(max_length=4096, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    stars = models.PositiveIntegerField(default=0, db_index=True)
    starred_by = models.ManyToManyField(
        Account, blank=True, related_name='starred_by')

    def __str__(self):
        return str(self.id)+' : '+self.heading[:50]+("..." if(len(self.heading) > 50) else "")


class Comment(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE)
    body = models.TextField(max_length=2048)
    created = models.DateTimeField(auto_now_add=True)
    votes = models.PositiveIntegerField(default=0)
    voted_by = models.ManyToManyField(
        Account, related_name='voted_by')

    def __str__(self):
        return str(self.id)+' : '+self.body[:50]+("..." if(len(self.body) > 50) else "")
