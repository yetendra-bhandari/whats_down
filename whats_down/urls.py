from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls'))
]

admin.site.site_header = "What's Down?"
admin.site.site_title = "What's Down?"
admin.site.index_title = "Administration"
