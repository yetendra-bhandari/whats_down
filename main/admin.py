from django.contrib import admin
from .models import Account, Post, Comment


class Created(admin.ModelAdmin):
    readonly_fields = ('created',)


admin.site.register(Account, Created)
admin.site.register(Post, Created)
admin.site.register(Comment, Created)
