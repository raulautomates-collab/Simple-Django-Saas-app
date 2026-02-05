from django.urls import path,include
from .views import * # Added space after 'from'

urlpatterns = [  # Corrected spelling to 'urlpatterns'
    path('', home_page_view, name='homepage'),
    path('home/',view=index,name='indexpage'),
    path('protected/useronly',view=user_only,name='useronly '),
     path('accounts/', include('allauth.urls')),
     path('base/',view=index,name='basepage'),
     path('protected/staffonly',view=staff_only,name='staffonly'),
]