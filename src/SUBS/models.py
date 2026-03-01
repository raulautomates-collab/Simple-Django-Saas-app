from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import Group,Permission
from django.conf import settings
from django.db.models.signals import post_save
from helpers import billing
from django.urls import reverse
from django.db.models import Q

#Custom Model managers for  Q lookups

class UserSubscriptionQueryset(models.QuerySet):


    #Model Managers
    def by_active_trialing(self):
         active_qs_lookup=(
         Q(status=SubscriptionStatus.ACTIVE),
         Q(status=SubscriptionStatus.TRIALING)
    )
         return self.filter(active_qs_lookup)
    
    def byuser_ids(self,user_ids=None):
        qs=self
        if isinstance(user_ids,list):
            qs=self.filter(user_id__in=user_ids)
        elif isinstance(user_ids,int):
            qs=self.filter(user_id__in=[user_ids])

        elif isinstance(user_ids,str):
            qs=self.filter(user_id__in=[user_ids])
        return qs
   

class UserSubscriptionManager(models.Manager):
     
    def get_queryset(self):
         return UserSubscriptionQueryset(self.model,using=self._db)
    
    #def by_user_ids(self,user_ids=None):
    #     return self.get_queryset().byuser_ids(user_ids=user_ids)




MyUser = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS=True
# Create your models here.
PERMISSIONS=[
        ('basic','Basic Perm'),
        ('Pro','Pro Perm'),
        ('advanced','Advanced Perm'),
        ('Enterprise','Enterprise Perm'),
    ]
#
 

class SubscriptionStatus(models.TextChoices):
         
         ACTIVE='active','Active',
         TRIALING='trialing','Trialing',
         INCOMPLETE='incomplete','Incomplete',
         INCOMPLETE_EXPIRED='incomplete_expired','Incomplete Expired',
         PAST_DUE='past_due','Past Due',
         CANCELLED='cancelled','Cancelled',
         UNPAID='unpaid','Unpaid',
         UNUSED='unused','Unused',


class Subscription(models.Model):
    name=models.CharField(max_length=20)
    groups=models.ManyToManyField(Group)#on to one->etc
    isactive=models.BooleanField(default=True)
    
    
    permissions=models.ManyToManyField(Permission,limit_choices_to={"codename__in":['basic',"pro",'advanced','Enterprise']
})
    
    stripe_id=models.CharField(max_length=120,blank=True,null=True)
    features=models.TextField(blank=True,null=True,help_text="Features for the individual subscription plans")
    
    

    #Alternative->"codename__in":['basic',"pro",'advanced' etc ...]

    class Meta:
        permissions=PERMISSIONS

    #return the faetures list as newline strings
    def get_features_as_list(self):
         if not self.features:
              return []
         return [x.strip()  for x in  self.features.split("\n")  ]  
 

    
    def __str__(self):
        return self.name    
    
    






#override the default save method to create stripe id    
    def save(self,*args,**kwargs):
        if not self.stripe_id:    
            
                    stripe_id=billing.create_product(
                        name=self.name,metadata={
                         
                            
                        },raw=False
                    )
                    self.stripe_id=stripe_id
        super().save(*args,**kwargs)
            

class MyUserSubscription(models.Model):


    
         
         
    
    user=models.OneToOneField(MyUser,on_delete=models.CASCADE)
    sub=models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True,blank=True)
    
    stripe_id=models.CharField(max_length=120,blank=True,null=True)
    active=models.BooleanField(default=True) #Check for active subscriptions
    user_cancelled=models.BooleanField(default=False)
    current_period_start=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    current_period_end=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    original_period_start=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    
    #->Ensuring the user has only one subscription
    status=models.CharField(choices=SubscriptionStatus.choices,max_length=20,blank=True,null=True)
    cancel_at_period_end=models.BooleanField(default=False)


    
   #1:OPTIONAL delay to start new subscription in checkout
   #https://docs.stripe.com/payments/checkout/billing-cycle
    @property
    def billling_cycle_anchor(self):
         if self.current_period_end:
              return int(self.current_period_end.timestamp())
         
    def serialize(self):
         return{
              'status':self.status,
              'current_period_start':self.current_period_start,
              'current_period_end':self.current_period_end,
              'plan_name':self.plan_name
         }

    def get_absolute_url(self):
         return reverse('mysubscription')
    

    def cancel_url(self):
         return reverse('cancelmysubscription')
  
    
    @property
    def is_activestatus(self):
         return self.status in[SubscriptionStatus.ACTIVE,SubscriptionStatus.TRIALING]

    def plan_name(self):
         if not self.sub:
              return None
         return self.sub.name
    

    def save(self,*args,**kwargs):
    # Set original_period_start only on first save when it's None
        
        if self.original_period_start is None and self.current_period_start is not None:
            self.original_period_start = self.current_period_start  # ← FIXED
            
        super().save(*args,**kwargs)
    


#->Subscription price model
class SubscriptionPrice(models.Model):
    #interval choices subclass

        DEFAULT_PRICE=19.99
        class IntervalChoices(models.TextChoices):
            MONTH='month','Month',
            YEAR='year','Year'

        
        featured=models.BooleanField(default=True)
        updated=models.DateTimeField(auto_now=True)
        timestamp=models.DateTimeField(auto_now_add=True)
        order=models.IntegerField(default=-1)
        subscription=models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True)                                             
        pricing_interval=models.CharField(max_length=120,choices=IntervalChoices.choices,default=IntervalChoices.MONTH)
        stripe_id=models.CharField(max_length=120,blank=True,null=True)
        price = models.DecimalField(
            max_digits=10, 
            decimal_places=2, 
            default=19.99, # type: ignore
        )
        
        
        def get_mycheckout_url(self):
         return reverse('sub_price_checkout',kwargs={'price_id':self.id}) # type: ignore->model id used




        @property
        def product_stripe_id(self):
            if not self.subscription:
                return None
            return self.subscription.stripe_id
        
        #pricing property
        @property
        def stripe_currency(self):
             return 'usd'
        
        @property
        def stripe_price(self):
            #remove decimal palaces
            return int(self.price*100)
        @property
        def display_sub_name(self):
             if not self.subscription:
                  return "Plan"
             return self.subscription.name
        
        #display the individual subscription features
        @property
        def display_features(self):
             if not self.subscription:
                  return []
             return self.subscription.get_features_as_list()
    #->overiding the default save method   

        
        def save(self,*args,**kwargs):
           if(not self.stripe_id and self.product_stripe_id is not None):
                                
                
                stripe_id =billing.create_price(
                    currency=self.stripe_currency,
                    unit_amount=self.stripe_price,
                    interval=self.pricing_interval,
                    product=self.product_stripe_id,
                    raw=False
                )
                self.stripe_id=stripe_id
           super().save(*args,**kwargs)
           if self.featured and self.subscription:
             qs=SubscriptionPrice.objects.filter(
                  subscription=self.subscription,
                  pricing_interval=self.pricing_interval
             ).exclude(id=self.id) # type: ignore
             qs.update(featured=False)    


def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.sub
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(isactive=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        # groups_ids = groups.values_list('id', flat=True) # [1, 2, 3] 
        current_groups = user.groups.all().values_list('id', flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_group_ids)


post_save.connect(user_sub_post_save, sender=MyUserSubscription)            