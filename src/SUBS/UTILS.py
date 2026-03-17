
from typing import Any


from SUBS.models import MyUserSubscription,Subscription,SubscriptionStatus,UserSubscriptionQueryset
from helpers import billing
from PROSPECTS.models import Customer
from django.db.models import Q


#1->Subscriptio refresh utility function

def refresh_active_user_subscriptons(user_ids=None):
    # Use __in lookup for cleaner code
    qs = MyUserSubscription.objects.filter(
    
# Option 1: Combine Q objects with OR operator (|)
# active_qs_lookup = (
#     Q(status=SubscriptionStatus.ACTIVE) | 
#     Q(status=SubscriptionStatus.TRIALING)
# )
# qs=MyUserSubscription.objects.filter(active_qs_lookup)

# Option 2: Unpack tuple of Q objects with *
# active_qs_lookup=(
#     Q(status=SubscriptionStatus.ACTIVE),
#     Q(status=SubscriptionStatus.TRIALING)
# )
# qs=MyUserSubscription.objects.filter(*active_qs_lookup)
   
        status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    )
    



    # Filter by user IDs
    if isinstance(user_ids, list):
        qs = qs.filter(user_id__in=user_ids)
    elif isinstance(user_ids, (int, str)):
        qs = qs.filter(user_id__in=[user_ids])

    complete_count = 0
    qs_count = qs.count()
    print(qs_count)
    
    for obj in qs: 
        if obj.stripe_id:
            sub_data = billing.get_subscription(obj.stripe_id, raw=False)
            for k, v in sub_data.items():  # ← Added ()
                setattr(obj, k, v)  # ← Fixed argument order
            obj.save() 
            complete_count += 1

    return complete_count == qs_count

def cleardanglingsubs():
        qs=Customer.objects.filter(stripe_id__isnull=False)
        for customer_obj in qs:
            user=customer_obj.user
            customer_stripe_id=customer_obj.stripe_id
            mycurrent_subs=billing.get_customeractive_subscription(customer_stripe_id)

            print(f"The customer id is {customer_stripe_id} ,the user is {user}")
            for sub in mycurrent_subs:
                existing_user_subs_qs=MyUserSubscription.objects.filter(stripe_id__iexact=f'{sub.id}'.strip())
                if existing_user_subs_qs.exists:
                    continue
                billing.cancel_subscription(sub.id,reason='dangling subscription',cancel_at_period_end=False)
                
                print(f'The user subs are listed below: The ids are{sub.id} .The dangling subs are {existing_user_subs_qs}')
                


def syncsubs_groups_perms():
     qs=Subscription.objects.filter(isactive=True)
     for obj in qs:
          sub_perms=obj.permissions.all()
          for groups in obj.groups.all():
               groups.permissions.set(sub_perms)