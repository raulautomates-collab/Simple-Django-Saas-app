

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
    return serialize_subscription_data(response.url)

#serialize sub data
def serialize_subscription_data(subscription_response):
    status=subscription_response.status
    current_period_start=date_utils.timestamp_as_datetime(subscription_response.current_period_start)
    current_period_end=date_utils.timestamp_as_datetime(subscription_response.current_period_end)


    return {
        'current_period_start':current_period_start,
        'current_period_end':current_period_end,
        'status':status
    }
                
#Correlating the user purchase with the user subscription all details are from stripe
def get_subscription_plan(session_id):
    checkout_r=get_checkout_session(session_id,raw=True)
    
    sub_stripe_id=checkout_r.subscription
    sub_r=get_subscription(sub_stripe_id,raw=True)
    customer_id=checkout_r.customer
    sub_plan=sub_r.plan
    
    
    return customer_id,sub_plan.id,sub_stripe_id

