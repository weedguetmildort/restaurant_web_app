from django.urls import path 
from . import views 
  
urlpatterns = [
    # User registration and token generation endpoints
    path('login', views.tokens)
]
