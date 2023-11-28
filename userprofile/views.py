from django.shortcuts import render,redirect,HttpResponseRedirect
from .forms import User_Profile
from django.contrib import messages
from django.contrib.auth.models import User
from userincome.models import Source
# Create your views here.

def userprofile(request):
    Sources=Source.objects.filter(owner=request.user)
    if request.user.is_authenticated:
        if request.method=="POST":
            form=User_Profile(data=request.POST,instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request,'Profile Updated Successfully!!')
        else:
            form=User_Profile(instance=request.user)
        return render(request,'userprofile/profile.html',{'form':form,'sources':Sources})
    else:
        messages.info(request,"You need to login first to view your profile")
        return HttpResponseRedirect('/authentication/login/')
    
def addSource(request):
    form=User_Profile(instance=request.user)
    if request.method=="POST":
        newSource=request.POST['Source']
        if Source.objects.filter(name=newSource,owner=request.user).exists():
            messages.warning(request,"Income source already Exists")
            return HttpResponseRedirect('/account/')
        if len(newSource)==0:
            return HttpResponseRedirect('/account/')
        newsourceadded=Source.objects.create(name=newSource, owner=request.user)
        newsourceadded.save()

        messages.success(request,'Source added successfully')
        return HttpResponseRedirect('/account/')
    
def deleteSource(request,id):
    obj=Source.objects.get(pk=id)
    Source.delete(obj)
    messages.success(request,"source deleted successfully")
    return HttpResponseRedirect('/account/')