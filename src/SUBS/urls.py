from django.urls import path
from .views import *

urlpatterns=[
    path('pricing',view=subview,name='pricing_cards'),
    path('pricing/<str:pricing_interval>/',view=subview,name='pricing_interval'),
    
    
]