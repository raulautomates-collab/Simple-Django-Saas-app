
from django.contrib import admin
from django.urls import path, include
from CHECKOUTS.views import *
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Visits.urls')),
    path('subs/', include('SUBS.urls')),
    # social media authentication urls
    path('accounts/', include('allauth.urls')),
    path('accounts/signup/', view=account_signup),
    path('profiles/', include('PROFILES.urls')),
    # CHECKOUT FOR STRIPE
    #1)->Product price redirect view
    path('checkout/sub_price/<int:price_id>',view=product_price_redirect_view,name='sub_price_checkout'), 
    path('checkout/start',view=checkout_redirect_view,name='stripe_checkout_start'), # type: ignore
    path('checkout/success',view=checkout_finalize_view,name='stripe_checkout_end'),
    
]

