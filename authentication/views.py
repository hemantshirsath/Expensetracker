from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import account_activation_token
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
# Create your views here.


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'emailerror': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'emailerror': 'sorry email in use, choose another one'}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'usernameerror': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'usernameerror': 'sorry username in use, choose another one'}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }
        try:
            with transaction.atomic():
                if not User.objects.filter(username=username).exists():
                    if not User.objects.filter(email=email).exists():
                        if len(password) < 6:
                            messages.error(request, 'Password too short')
                            return render(request, 'authentication/register.html', context)
                        user = User.objects.create_user(
                            username=username, email=email)
                        user.set_password(password)
                        user.is_active = False
                        user.save()
                        email_subject = "Activate Your account"
                        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                        domain = get_current_site(request).domain
                        link = reverse('activate', kwargs={
                            'uidb64': uidb64, 'token': account_activation_token.make_token(user)
                        })
                        activate_url = 'http://'+domain+link
                        email_body = 'Hi ' + user.username + \
                            ' please use this link to verify your account\n'+activate_url
                        email = EmailMessage(
                            email_subject,
                            email_body,
                            'hemantshirsath24@gmail.com',
                            [email],
                        )
                        email.send(fail_silently=False)
                        messages.success(
                            request, 'Account created successfully. An email with activation link has been sent to your email.')
                    return render(request, 'authentication/register.html')
        except Exception as e:
            messages.error(request, "Error Occured : "+str(e))
        return render(request, 'authentication/register.html', context)


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, "Welcome, " +
                                     user.username + " you are now logged in")
                    return redirect('expenses')
                messages.error(
                    request, 'Account is not active, Please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, "Invalid credentials, try again")
            return render(request, "authentication/login.html")
        messages.error(request, "Please fill all fields")
        return render(request, "authentication/login.html")


class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated Successfully')
            return redirect('login')
        except Exception as e:
            pass
        return redirect('login')



class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            auth.logout(request)
            messages.success(request, "You have been logged out")
            return redirect('login')
        else:
            return redirect('login')
