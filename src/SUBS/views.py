from django.shortcuts import render,redirect
from django.urls import reverse
from cfehome.urls import product_price_redirect_view
from django.contrib.auth.decorators import login_required
from helpers import billing

from .models import *


# Create your views here.
def subview(request,pricing_interval="month"):
    qs=SubscriptionPrice.objects.filter(featured=True)
    inv_month=SubscriptionPrice.IntervalChoices.MONTH
    inv_year=SubscriptionPrice.IntervalChoices.YEAR
    active=inv_month
    url_path_name='pricing_interval'
    checkout_url='sub_price_checkout'
    
    monthly_url=reverse(url_path_name,kwargs={'pricing_interval':inv_month})
    yearly_url=reverse(url_path_name,kwargs={'pricing_interval':inv_year})
    
    object_list=qs.filter(pricing_interval=inv_month)
    if pricing_interval == inv_year:
         active=inv_year
         object_list=qs.filter(pricing_interval=SubscriptionPrice.IntervalChoices.YEAR)
    
    context={
      'object_list':object_list,
      'monthly_url':monthly_url,
      'yearly_url':yearly_url,
      'active':active,
      'checkout_url':checkout_url
    }

    
    return render(request,'snippet.html',context)

@login_required
def user_subscription_view(request):
     #1->Grab subscription aaaand user objects
     user_sub_obj,created=MyUserSubscription.objects.get_or_create(user=request.user)
     sub_data=user_sub_obj.serialize()
     #2->Refresh Subscriptions status
     if request.method=='POST':
          print('Refresh Homie')
     #3->Store subscription status for the users            
          if user_sub_obj.stripe_id:
               sub_data=billing.get_subscription(user_sub_obj.stripe_id,raw=False)
               for k,v in sub_data.items():
                    setattr(user_sub_obj,k,v)
     
          return redirect(user_sub_obj.get_absolute_url())
     context={
          'subscription':user_sub_obj
     }

     return render(request,'user_detailview.html',context)