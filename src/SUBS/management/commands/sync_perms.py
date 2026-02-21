from typing import Any
from django.core.management.base import BaseCommand
from SUBS.models import Subscription
from PROSPECTS.models import Customer
from helpers import billing
#Sync all customers and their subscriptions for cancelling dnagling user subscriptions
class Command(BaseCommand):#basic hello world function
        def handle(self,*args:Any,**options:Any):
            qs=Customer.objects.all()    
            for customer_obj in qs:
                  user=customer_obj.user
                  customer_stripe_id=customer_obj.stripe_id
                  print(f"sync :{user} with id: {customer_stripe_id}  and remove old ones")
                  print('Homie ,you trippin,gay ass motherfuc**er')

                  

    
        


  