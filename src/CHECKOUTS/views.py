from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from SUBS.models import SubscriptionPrice
from helpers import billing
from django.urls import reverse
from django.conf import settings


BASE_URL=settings.BASE_URL


def product_price_redirect_view(request,price_id=None,*args,**kwargs):
    request.session['checkout_subscription_price_id']=price_id
    return redirect('stripe_checkout_start')

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id=request.session.get('checkout_subscription_price_id')
    try:
        obj=SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj=None
    if checkout_subscription_price_id is None or obj is None:
        return redirect('subs/pricing')    
    customer_stripe_id=request.user.customer.stripe_id
    success_url_path=reverse('stripe_checkout_end')
    success_url_base=BASE_URL
    success_url=f"{BASE_URL}{success_url_path}"
    pricing_url_path=reverse('pricing_cards')
    return_url=f"{BASE_URL}{pricing_url_path}"
    price_stripe_id=obj.stripe_id

    print(customer_stripe_id)
    url=billing.start_checkout_session(
         customer_id=customer_stripe_id,
         success_url=success_url,
         cancel_url=return_url,
         price_stripe_id=price_stripe_id, # type: ignore
         raw=False,

    )
    return redirect(url) # type: ignore


def checkout_finalize_view(request):
    session_id=request.Get.get('session_id')
    session_response=billing.get_checkout_session(session_id,raw=True)
    #linking the sbubscriptioncheckout session with the subscription model

    
    sub_stripe_id=session_response.subscription # type: ignore
    sub_response=billing.get_subscription(session_id,raw=True)
    print(sub_response)
    print(session_response)
    context={
        'subscription':sub_response,
        'checkout':session_response
    }

    return render(request,'checkoutsuccess.html',context)