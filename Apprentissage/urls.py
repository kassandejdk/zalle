from django.conf.urls.static import static
from Apprentissage import settings
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('utilisateurs.urls')),
 
    path('cours/',include('cours.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

