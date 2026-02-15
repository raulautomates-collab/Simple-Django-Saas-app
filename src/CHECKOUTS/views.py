from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from SUBS.models import SubscriptionPrice,MyUserSubscription,Subscription
from helpers import billing
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest,HttpResponse



BASE_URL=settings.BASE_URL
User=get_user_model()


def product_price_redirect_view(request,price_id=None,*args,**kwargs):
    request.session['checkout_subscription_price_id']=price_id #associate the stripe id with login required
    return redirect('stripe_checkout_start')

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id=request.session.get('checkout_subscription_price_id')
    try:
        obj=SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj=None
    if checkout_subscription_price_id is None or obj is None:
        return redirect('subs/pricing')  #redirect to pricing page  
    customer_stripe_id=request.user.customer.stripe_id #grab the stripe id from the customer
    print(customer_stripe_id)

    #urls for checkouts
    success_url_path=reverse('stripe_checkout_end')
    
    success_url=f'{BASE_URL}{success_url_path}?session_id={{CHECKOUT_SESSION_ID}}'  # Note the {{ }}' #combine the base url and success url path

   #1->Always append the checkout session id to the end of the session to avoid id None type error see line 34 above
    pricing_url_path=reverse('pricing_cards')
    cancel_url=f"{BASE_URL}{pricing_url_path}"

    price_stripe_id=obj.stripe_id

    url=billing.start_checkout_session(
        customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=price_stripe_id,
        raw=False

    )
    return redirect(url)

    

def checkout_finalize_view(request):
    session_id=request.GET.get('session_id')
    checkout_data=billing.get_subscription_plan(session_id)
    plan_id=checkout_data.pop('plan_id')
    customer_id=checkout_data.pop('customer_id')
    sub_stripe_id=checkout_data.pop('sub_stripe_id')
    subscription_data={**checkout_data}
    #->Subscription related lookups
    try:
        sub_obj=Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj=None

    #2->User related lookups
    try:
        user_obj=User.objects.get(customer__stripe_id=customer_id)  

    except:
        user_obj=None
    user_sub_exists=False
    updated_sub_options={
        'sub':sub_obj,
        'stripe_id':sub_stripe_id,
        'user_cancelled':False,
        **subscription_data
        
    }
    #3->Create the actual user object and save
    try:
        user_sub_obj=MyUserSubscription.objects.get(user=user_obj)
        user_sub_exists=True

    except MyUserSubscription.DoesNotExist:
        user_sub_obj=MyUserSubscription.objects.create(user=user_obj,**updated_sub_options)

    except:
        user_sub_obj=None
    if None in [user_obj,sub_obj,user_sub_obj]:
        return HttpResponseBadRequest('There was an error with your account.Please contact us')  

    #4-> save the user object
    if user_sub_exists:
        #5=>Cancel old subs
        old_stripe_id=user_sub_obj.stripe_id #avoid removing recently added subscriptions
        same_stripe_id=sub_stripe_id==old_stripe_id
        if old_stripe_id is not None and not same_stripe_id:
             try:
                billing.cancel_subscription(old_stripe_id,reason='Auto ended new membership ',feedback='other')
             except:
                 pass  
        #6=>Assign new subs
        for k,v in updated_sub_options:
            setattr(user_sub_obj,k,v)
        
        user_sub_obj.save()

    return render(request, 'checkoutsuccess.html', {})
