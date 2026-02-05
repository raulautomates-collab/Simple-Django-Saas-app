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
    user=models.OneToOneField(MyUser,on_delete=models.CASCADE)
    sub=models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True,blank=True)
    isactive=models.BooleanField(default=True)





#subscription sgnals and signal relationshps
#Checks for whwn the subscription is changed and grabs the associated groups
def user_sub_post_save(sender,instance,*args,**kwargs):
     user_sub_instance=instance
     user=user_sub_instance.user
     subscription_obj=user_sub_instance.subscription
     groups=subscription_obj.groups.all()
     user.groups.set(groups)
     if ALLOW_CUSTOM_GROUPS==False:
         user.groups.set(groups)
     else:
          subs_qs=Subscription.objects.filter(isactive=True).exclude(id=subscription_obj.id)
          subs_groups=subs_qs.values_list('groups__id',flat=True)
          subs_groups_set=set(subs_groups)
          groups_ids=groups.values_list('id',flat=True) 
             #return a list of groups
          current_groups=user.groups.all().values_liSt('id',flat=True)
          groups_ids_set=(groups_ids) 
          current_groups_set=set(current_groups)-subs_groups_set
          final_group_ids=list(groups_ids_set|current_groups_set)
          user.groups.set(groups_ids)

post_save.connect(user_sub_post_save,sender=MyUserSubscription)
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
         return reverse('sub_price_checkout',kwargs={'price_id':self.id}) # type: ignore




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