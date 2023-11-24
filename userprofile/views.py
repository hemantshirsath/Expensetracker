from django.shortcuts import render,redirect,HttpResponseRedirect
from .forms import User_Profile
from django.contrib import messages
from django.contrib.auth.models import User
# Create your views here.
def userprofile(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            form=User_Profile(data=request.POST,instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request,'Profile Updated Successfully!!')
        else:
            form=User_Profile(instance=request.user)
        return render(request,'userprofile/profile.html',{'form':form})
    else:
        messages.info(request,"You need to login first to view your profile")
        return HttpResponseRedirect('/authentication/login/')