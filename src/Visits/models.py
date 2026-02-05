from django.db import models

# Create your models here.
#pagevisit model
class PageVisit(models.Model):
    #id=primarykey etc
    name=models.CharField(max_length=30)
    timestamp=models.DateTimeField(auto_now_add=True)
    approved=models.BooleanField(default=True)
    path=models.TextField(null=True,blank=True)
    
    


    def __str__(self):
        return self.name
