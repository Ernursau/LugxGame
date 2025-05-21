"""
URL configuration for DjangoProject22 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.core.management import call_command

from django.http import HttpResponse
from django.core.management import call_command

def setup_view(request):
    try:
        call_command("migrate", interactive=False)
        call_command("collectstatic", interactive=False, verbosity=0)
        return HttpResponse("✅ migrate и collectstatic выполнены")
    except Exception as e:
        return HttpResponse(f"❌ Ошибка: {e}")



def collectstatic(request):
    try:
        call_command("collectstatic", interactive=False, verbosity=0)
        return HttpResponse("✅ collectstatic выполнен успешно")
    except Exception as e:
        return HttpResponse(f"❌ Ошибка: {e}")



urlpatterns = [

    path('static-setup/', collectstatic),
    path("setup/", setup_view),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
