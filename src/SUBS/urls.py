from django.urls import path
from .views import *

urlpatterns=[
    path('pricing',view=subview,name='pricing_cards'),
    path('pricing/<str:pricing_interval>/',view=subview,name='pricing_interval'),
    path('accounts/billing',view=user_subscription_view,name='mysubscription'),
    path('accounts/cancel/',view=user_subscription_cancel_view,name='cancelmysubscription')
    
    
]