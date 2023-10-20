from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
import datetime
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)

    sort_order = request.GET.get('sort')

    if sort_order == 'amount_asc':
        income = income.order_by('amount')
    elif sort_order == 'amount_desc':
        income = income.order_by('-amount')
    elif sort_order == 'date_asc':
        income = income.order_by('date')
    elif sort_order == 'date_desc':
        income = income.order_by('-date')

    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    total = page_obj.paginator.num_pages
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        'total': total,
        'sort_order': sort_order,
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        date_str = request.POST.get('income_date')
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        try:
            # Convert the date string to a datetime object and validate the date
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'income/add_income.html', context)
                # return redirect('add-income', context)

            UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                      source=source, description=description)
            messages.success(request, 'Income saved successfully')

            return redirect('income')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'income/add_income.html', context)
            # return redirect('add-income', context)

        # UserIncome.objects.create(owner=request.user, amount=amount, date=date,
        #                           source=source, description=description)
        # messages.success(request, 'Record saved successfully')

        # return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        date_str = request.POST.get('income_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)

        try:
            # Convert the date string to a datetime object and validate the date
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'income/edit_income.html', context)
                # return redirect('edit_income', context)

            income.amount = amount
            income. date = date
            income.source = source
            income.description = description
            income.save()
            messages.success(request, 'Income saved successfully')

            return redirect('income')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'income/edit_income.html', context)
        # income.amount = amount
        # income. date = date
        # income.source = source
        # income.description = description

        # income.save()
        # messages.success(request, 'Record updated  successfully')

        # return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')
