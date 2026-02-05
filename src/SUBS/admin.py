from django.contrib import admin

# Register your models here.
from .models import Subscription,SubscriptionPrice,MyUserSubscription

#display subscription price as tabular inline fields


class SubscriptionPriceAdmin(admin.TabularInline):
    model=SubscriptionPrice
    readonly_fields=['stripe_id']
    extra=0

class SubscriptionAdmin(admin.ModelAdmin):
    inlines=[SubscriptionPriceAdmin]
    list_display=['name','isactive']


admin.site.register(Subscription,SubscriptionAdmin)
admin.site.register(MyUserSubscription)