# Necessary imports
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # URL configuration for LittleLemon project
    path('admin/', admin.site.urls),
    path('api/', include('LittleLemonAPI.urls')),
    path('token/', include('LittleLemonAPI.tokens')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
