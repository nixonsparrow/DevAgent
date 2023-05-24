from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from manager.views import error_404, error_403, error_500

urlpatterns = [
    path("", include("users.urls")),
    path("", include("manager.urls")),
    path("admin/", admin.site.urls),
]

handler403 = error_403
handler404 = error_404
handler500 = error_500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
