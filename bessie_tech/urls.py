from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import Group
from bessie.views import index
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_title = "Bessie site admin"
admin.site.site_header = "Bessie administration"
admin.site.index_title = "Site administration"
admin.site.unregister(Group)

urlpatterns = [
    path("", include("pages.urls")),
    path('dashboard/', index, name='dashboard'),
    path("admin/", admin.site.urls),
    path("take-bessie/", include("bessie.urls")),
    path("mini-bessie/", include("mini_bessie.urls")),
    path("accounts/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
