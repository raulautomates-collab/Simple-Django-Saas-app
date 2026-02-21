

import stripe
from pathlib import Path
import os
from dotenv import load_dotenv
from . import date_utils



load_dotenv()

STRIPE_SECRET_KEY = str(os.environ.get('STRIPE_SECRET_KEY'))

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(name="", email="",metadata={} ,raw=False):
    #stripe customer object from stripe.com
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata
        
    )
    if raw:
        return response#return the response id 
    stripe_id = response.id
    return stripe_id
#create product object

def create_product(name="",metadata={},raw=False):
    
    
    product = stripe.Product.create(name=name,metadata=metadata)
    if raw:
        return product
    product_id = product.id
    return product_id
    

def create_price(currency='usd',
                    unit_amount=9999,
                    interval='month',
                    product=None,
                    metadata={},
                    raw=False
                    ):
    if product is None:
        return None
    response=stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        product=product,
        metadata=metadata,
        recurring={'interval':'month'}
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id
#create stripe checkout session


def start_checkout_session(customer_id,success_url="",cancel_url="",price_stripe_id="",raw=True):
    response = stripe.checkout.Session.create(
        success_url=success_url,
        line_items=[{"price":price_stripe_id, "quantity": 1}],
        mode="subscription",
        cancel_url=cancel_url,
        customer=customer_id
    )
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):#stripe urlapi variable naming
        success_url=f"{success_url}"+"session_id={CHECKOUT_SESSION_ID}"
    if raw:
        return response
    return response.url
    
#RETRIEVE A CUSTOMER SESSION

def get_checkout_session(stripe_id,raw=True):
    response=stripe.checkout.Session.retrieve(
        stripe_id
    )

    if raw:
        return response
    return response.url
    
#->Retrieve a subscription

def get_subscription(stripe_id,raw=True):
    response=stripe.Subscription.retrieve(stripe_id)
    
    if raw:
        return response
    return serialize_subscription_data(response)

#serialize sub data
def serialize_subscription_data(subscription_response):
    status=subscription_response.status
    
    current_period_start=date_utils.timestamp_as_datetime(subscription_response["items"]["data"][0]["current_period_start"])

    cancel_at_period_end=subscription_response.cancel_at_period_end
    current_period_end=date_utils.timestamp_as_datetime(subscription_response["items"]["data"][0]["current_period_end"])

    return {
        'current_period_start':current_period_start,
        'current_period_end':current_period_end,
        'status':status,
        'cancel_at_period_end':cancel_at_period_end
    }
                
#correlating the subscriptions from stripe with the user subscriprion model
def get_subscription_plan(session_id):
    checkout_r=get_checkout_session(session_id,raw=True)
    
    sub_stripe_id=checkout_r.subscription
    sub_r=get_subscription(sub_stripe_id,raw=True)
    customer_id=checkout_r.customer
    sub_plan=sub_r.plan
    
    subscription_data=serialize_subscription_data(sub_r)
    
    current_period_start=date_utils.timestamp_as_datetime(sub_r["items"]["data"][0]["current_period_start"])
 

    current_period_end=date_utils.timestamp_as_datetime(sub_r["items"]["data"][0]["current_period_end"])
    print(f'The current period start is {current_period_start}')

    print(f'The current period start is {current_period_end}')
    data={
        'customer_id':customer_id,
        'plan_id':sub_plan.id,
        'sub_stripe_id':sub_stripe_id,
        'current_period_start':current_period_start,
        'current_period_end':current_period_end
        
    }
    
    return data




def cancel_subscription(stripe_id,reason="",cancel_at_period_end=False,feedback="other",raw=True):
    if cancel_at_period_end:

        #Cancel dnagling user subs
        response=stripe.Subscription.cancel(
        stripe_id,
        cancel_at_period_end=cancel_at_period_end,  
        cancellation_details={
            'comment':reason,
            'feedback':feedback
        }
    )
    else:
        response=stripe.Subscription.cancel(
        stripe_id,
        cancellation_details={
            'comment':reason,
            'feedback':feedback
        }
    )


    if raw:
        return response
    return serialize_subscription_data(response)


