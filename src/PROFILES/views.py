from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()

# user permissions view=
@login_required  # checking if user is logged in
def profileview(request,username=None):
    user=request.user  
    usergroups=user.groups.all()
    #define user using group relationships
    profile_user_obj=get_object_or_404(User,username=username)
    owner=profile_user_obj==user
    
    context={
        'is_me':owner,
        'profile_user_obj':profile_user_obj
    }


    return render(request, 'profile.html', context)

# user list view
@login_required
def listusers(request):
    myusers = User.objects.all()
    activesusers = User.objects.filter(is_active=True)
    
    context = {
        'myusers': myusers,
        'activesusers':activesusers,
       
    }
    return render(request, 'listingpage.html', context) 
    

def marvel(request):
    return render(request, 'marvel.html')