from django.shortcuts import render,redirect
from django.urls import reverse
from cfehome.urls import product_price_redirect_view
from django.contrib.auth.decorators import login_required
from helpers import billing
from django.contrib import messages

from .models import Subscription,SubscriptionPrice,MyUserSubscription
from SUBS import UTILS


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
     user_sub_obj,created=MyUserSubscription.objects.get_or_create(user=request.user)
     #Create a checkout page if they don't have one
     sub_data=user_sub_obj.serialize() #For Django rest framework apis
     if request.method=="POST":
     #Refresh active user subscriptions
          finished=UTILS.refresh_user_subs(user_ids=request.user.id,active_only=False)    
          if finished:
               messages.success(request,'Your Plan Details have been succesfully updated ')
          else:
               messages.error(request,'Your Plan details have not been refreshed,Please try again')     
          
     #redirect after form submission
          return redirect(user_sub_obj.get_absolute_url())           
     context={
          'mysubscription':user_sub_obj
     }        
     return render(request,'user_detailview.html',context)


@login_required
def user_subscription_cancel_view(request):

     user_sub_obj,created=MyUserSubscription.objects.get_or_create(user=request.user)
     #Create a checkout page if they don't have one
     sub_data=user_sub_obj.serialize() #For Django rest framework apis
     if request.method=="POST":
          
          if user_sub_obj.stripe_id and user_sub_obj.is_activestatus: #only cancel an active subscription
               sub_data=billing.cancel_subscription(
                    user_sub_obj.stripe_id,
                    reason="The subscription was a piece of shite",
                    raw=False,
                    feedback='other',
                    cancel_at_period_end=True
               
               )
                                                    
          #for ease of reausability                                          
               for k,v in sub_data.items():
                    setattr(user_sub_obj,k,v)
               user_sub_obj.save()   
               messages.success(request,'Your Plan Has been cancelled')  

     #redirect after form submission
          return redirect(user_sub_obj.get_absolute_url())     
           
     context={
          'mysubscription':user_sub_obj
     }        
     

     return render(request,'user_cancelview.html',context)

