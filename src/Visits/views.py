

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import pathlib



def home_page_view(request,*args,**kwargs):
    
    return render(request,'home.html')
def index(request):
    queryset=PageVisit.objects.all()
    try:
        percent=(queryset.count()*100.0/queryset.count())
    except:
        percent=0    
    html_template='base.html'
    page_title='basehtmlpage'
    context={
        'my_title':page_title,
        'page_visit_count':queryset.count(),
        'percent':percent
         
    }
    PageVisit.objects.create()
    return render(request,html_template,context)


    
@login_required
def user_only(request):
    return render(request,'about.html') 

@staff_member_required
def staff_only(request):
    return render(request,'about.html') 
