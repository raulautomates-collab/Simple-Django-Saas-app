from django.urls import path
from . import views
from django.contrib.auth import get_user_model



User = get_user_model()

urlpatterns = [
    path('profiles/<username>/', views.profileview, name='profile'),  
    path('list/', views.listusers, name='list_users'),
    path('marvel/', views.marvel, name='marvel')
]
 