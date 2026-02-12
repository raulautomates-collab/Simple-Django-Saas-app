from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from helpers import billing
from allauth.account.signals import(
   user_signed_up as allauth_user_signed_up,
   email_confirmed as allauth_email_confirmed
)

# Create your models here.

User=settings.AUTH_USER_MODEL

class Customer(models.Model):
   user=models.OneToOneField(User,on_delete=models.CASCADE)
   init_email=models.EmailField(blank=True,null=True)
   init_email_confirmed=models.BooleanField(default=False)
   stripe_id=models.CharField(max_length=60,null=True,blank=True)
   

   def __str__(self):
      return f"{self.user.username}"

   def save(self,*args,**kwargs):
      
      email=self.user.email
      if not self.stripe_id:
        if self.init_email and self.init_email_confirmed:
            email=self.init_email
            if email!="" or email is not None:
                
            
                stripe_id=billing.create_customer(
                    raw=False,
                    email=email,
                    metadata={'user_id':self.user.id}
                    
                )
                self.stripe_id=stripe_id
      super().save(*args,**kwargs)


def allauth_usersigned_up_handler(request,user,*args,**kwargs):
   email=user.email
   Customer.objects.create(
      user=user,
      init_email=email,
      init_email_confirmed=False,
   )

allauth_user_signed_up.connect(allauth_usersigned_up_handler)


def allauthemail_confirmed_handler(request, email_address,*args,**kwargs):
   qs=Customer.objects.filter(
      
      init_email=email_address,
      init_email_confirmed=False
   )
   for obj in qs:
      obj.init_email_confirmed=True
      #send the signal->qs.update()
      obj.save()

allauth_email_confirmed.connect(allauthemail_confirmed_handler)