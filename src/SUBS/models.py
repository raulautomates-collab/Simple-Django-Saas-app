from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import Group,Permission
from django.conf import settings
from django.db.models.signals import post_save
from helpers import billing
from django.urls import reverse

MyUser = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS=True
# Create your models here.
PERMISSIONS=[
        ('basic','Basic Perm'),
        ('Pro','Pro Perm'),
        ('advanced','Advanced Perm'),
        ('Enterprise','Enterprise Perm'),
    ]

 
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


    class SubscriptionStatus(models.TextChoices):
         
         ACTIVE='active','Active',
         TRIALING='trialing','Trialing',
         INCOMPLETE='incomplete','Incomplete',
         INCOMPLETE_EXPIRED='incomplete_expired','Incomplete Expired',
         PAST_DUE='past_due','Past Due',
         CANCELLED='cancelled','Cancelled',
         UNPAID='unpaid','Unpaid',
         UNUSED='unused','Unused',
    
    user=models.OneToOneField(MyUser,on_delete=models.CASCADE)
    sub=models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True,blank=True)
    isactive=models.BooleanField(default=True)
    stripe_id=models.CharField(max_length=120,blank=True,null=True)
    active=models.BooleanField(default=True) #Check for active subscriptions
    user_cancelled=models.BooleanField(default=False)
    current_period_start=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    current_period_end=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    original_period_start=models.DateTimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    
    #->Eansuring the user has only one subscription
    status=models.CharField(choices=SubscriptionStatus.choices,max_length=20,blank=True,null=True)

    #Subscription time anchors ->Optional delay to start new subscription in stripe
     

    



#subscription signals and signal relationshps
#Checks for when the subscription is changed and grabs the associated groups

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