
from typing import Any


from SUBS.models import MyUserSubscription,Subscription,SubscriptionStatus
from helpers import billing
from PROSPECTS.models import Customer
from django.db.models import Q



#Refresh subscription utility function

def refresh_user_subs(user_ids=None,active_only=True):
    
    #Refresh for more than one user
    #Triggers the save method if things change

    active_qs_lookup=(
         Q(status=SubscriptionStatus.ACTIVE),
         Q(status=SubscriptionStatus.TRIALING)
    )
    qs=MyUserSubscription.objects.all()
    if active_only:
       qs=qs.by_active_trialing()
    if user_ids is not None:
         qs=qs.by_user_ids(user_ids=user_ids)
    complete_count=0     
    qs_count=qs.count()

    for obj in qs:

        
        if obj.stripe_id:
                sub_data=billing.get_subscription(obj.stripe_id,raw=False)  
                for k,v in sub_data.items():
                        setattr(obj,k,v)
                obj.save()
        complete_count+=1
    return complete_count==qs_count          
                


def cleardanglingsubs():
    qs=Customer.objects.filter(stripe_id__isnull=False)
    for customer_obj in qs:
            user=customer_obj.user
            customer_stripe_id=customer_obj.stripe_id
            print(f"sync {user} with stripe id {customer_stripe_id} subs and remove their old ones")
            #Get all available user subs and list them
            user_subs=billing.get_customeractive_subscription(customer_stripe_id)
            for user_sub in user_subs:
             #Filter the existing stripe id
             existing_user_subs_qs=MyUserSubscription.objects.filter(stripe_id__iexact=f"{user_sub.id}".strip())
             print(user_sub.id)
             #Avoid cancelling active subscription
             if existing_user_subs_qs.exists:
                continue
             billing.cancel_subscription(user_sub.id,reason="Dangling usr subscription",cancel_at_period_end=True)
             #CANCEL AT PERIOD END CAN BE FALSE
             print(user_sub.id,existing_user_subs_qs.exists())

def syncsub_groups_perms():
    #1->Sync all permissions
        
    qs=Subscription.objects.filter(isactive=True)
    for obj in qs:
        sub_perms=obj.permissions.all()
        for group in obj.groups.all():
          group.permissions.set(sub_perms)
          #for per in obj.permissions.all()
          # group.permissions.add(per)
          #print(obj.permissions.all())