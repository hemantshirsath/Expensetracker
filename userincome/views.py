from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta


from django.shortcuts import render, redirect,HttpResponseRedirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import UserIncome
from expenses.models import Expense
from django.db.models import Sum
import csv
import openpyxl
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa


from .models import UserIncome
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from datetime import datetime
# Create your views here.

@login_required(login_url='/authentication/login')

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
    categories = Source.objects.filter(owner=request.user)
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
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency=None
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
    sources = Source.objects.filter(owner=request.user)
    if(len(sources)==0):
        messages.info(request,"you need to add income sources first in order to add income")
        return HttpResponseRedirect('/account/')
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
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.now().date()

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
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.now().date()

          
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

@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')


@login_required(login_url='/authentication/login')
def income_summary(request):
    user = request.user  # Get the logged-in user

    today = timezone.now()
    one_week_ago = today - timedelta(days=7)
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(month=1, day=1)

    # Query the database to get daily, weekly, monthly, and yearly income for the logged-in user
    daily_income = user.userincome_set.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    weekly_income = user.userincome_set.filter(date__range=[one_week_ago, today]).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_income = user.userincome_set.filter(date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_income = user.userincome_set.filter(date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'daily_income': daily_income,
        'weekly_income': weekly_income,
        'monthly_income': monthly_income,
        'yearly_income': yearly_income,
        # You can add more context data here if needed
    }
    return render(request, 'income/dashboard.html', context)

# @login_required(login_url='/authentication/login')
# def income_summary(request):
#     today = timezone.now()

#     # Calculate the date for one week ago
#     one_week_ago = today - timedelta(days=7)

#     # Calculate the first day of the current month
#     first_day_of_month = today.replace(day=1)
#     first_day_of_year = today.replace(month=1, day=1)

#     # Query the database to get daily, weekly, and monthly income
#     daily_income = UserIncome.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
#     weekly_income = UserIncome.objects.filter(date__range=[one_week_ago, today]).aggregate(Sum('amount'))['amount__sum'] or 0
#     monthly_income = UserIncome.objects.filter(date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
#     yearly_income = UserIncome.objects.filter(date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
#     context = {
#         'daily_income': daily_income,
#         'weekly_income': weekly_income,
#         'monthly_income': monthly_income,
#         'yearly_income': yearly_income,
#         # You can add more context data here if needed
#     }
#     return render(request,'income/dashboard.html',context)




from datetime import datetime

def monthly_income_data(request):
    # Get the current year
    current_year = datetime.now().year

    # Initialize a list to store monthly income data for the current year
    monthly_income_data = [0] * 12  # Initialize with zeros for 12 months

    # Get the monthly income data for the current year, grouped by month
    monthly_data = (
        UserIncome.objects
        .filter(date__year=current_year)  # Filter for the current year
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total_income=Sum('amount'))
        .order_by('month')
    )

    # Populate the list with the income data
    for item in monthly_data:
        month_index = item['month'] - 1  # Subtract 1 to convert month to zero-based index
        monthly_income_data[month_index] = item['total_income']

    # Return the data as JSON
    return JsonResponse({'monthly_income_data': monthly_income_data})







@login_required(login_url='/authentication/login')
def get_monthly_income(request):
    today = date.today()
    first_day_of_year = today.replace(month=1, day=1)
    last_day_of_year = today.replace(month=12, day=31)

    # Create a list to hold income data for all 12 months
    monthly_data = [0] * 12

    # Retrieve and fill in the actual monthly income data
    income_data = UserIncome.objects.filter(
        date__range=(first_day_of_year, last_day_of_year),
        owner=request.user
    ).values('date', 'amount')

    for entry in income_data:
        month = entry['date'].month - 1  # Convert month (1-12) to index (0-11)
        monthly_data[month] = entry['amount']

    return JsonResponse({'monthly_data': monthly_data})





def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="expense_report.pdf"'
        return response
    return HttpResponse("Error rendering PDF", status=400)


def export_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    incomes = UserIncome.objects.filter(date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date])
    
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    savings = total_income - total_expense
    
    context = {
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'savings': savings,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    pdf = render_to_pdf('income/pdf_template.html', context)
    return pdf

@login_required(login_url='/authentication/login')
def report(request):
    report_generated=False
    return render(request, 'income/report.html',{'report_generated':report_generated})

def generate_report(request):
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        user = request.user
        report_generated=True

        if start_date > end_date:
            messages.error(request, "Start date cannot be greater than end date.")
            return redirect('report')

        # incomes = UserIncome.objects.filter(date__range=[start_date, end_date])
        # expenses = Expense.objects.filter(date__range=[start_date, end_date])

        incomes = UserIncome.objects.filter(owner=user, date__range=[start_date, end_date])
        expenses = Expense.objects.filter(owner=user, date__range=[start_date, end_date])

        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        savings = total_income - total_expense
        
        context = {
            'incomes': incomes,
            'expenses': expenses,
            'total_income': total_income,
            'total_expense': total_expense,
            'savings': savings,
            'start_date': start_date,
            'end_date': end_date,
            'report_generated':report_generated
        }

        return render(request, 'income/report.html', context)
    else:
        
        return render(request, 'income/report.html')

def export_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    incomes = UserIncome.objects.filter(date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date])
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{start_date}_to_{end_date}.csv'
    
    writer = csv.writer(response)
    
    # Label the income section
    writer.writerow(['Income'])
    writer.writerow(['Date', 'Source', 'Amount'])
    
    income_total = 0
    for income in incomes:
        writer.writerow([income.date, income.source, income.amount])
        income_total += income.amount
    
    # Display the total income
    writer.writerow(['', f'Total Income: {income_total}'])

    # Label the expense section
    writer.writerow(['Expenses'])
    writer.writerow(['Date', 'Category', 'Amount'])
    
    expense_total = 0
    for expense in expenses:
        writer.writerow([expense.date, expense.category, expense.amount])
        expense_total += expense.amount
    
    # Add an empty line
    writer.writerow([])
    
    # Display the total expense
    writer.writerow(['', f'Total Expenses: {expense_total}'])
    
    return response

def export_xlsx(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    incomes = UserIncome.objects.filter(date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date])
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="report_{start_date}_to_{end_date}.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Label the income section
    ws.append(['Income'])
    ws.append(['Date', 'Source', 'Amount'])
    
    income_total = 0
    for income in incomes:
        ws.append([income.date, income.source, income.amount])
        income_total += income.amount
    
    # Display the total income
    ws.append(['', f'Total Income: {income_total}'])

    # Label the expense section
    ws.append(['Expenses'])
    ws.append(['Date', 'Category', 'Amount'])
    
    expense_total = 0
    for expense in expenses:
        ws.append([expense.date, expense.category, expense.amount])
        expense_total += expense.amount
    
    # Add an empty line
    ws.append([])
    
    # Display the total expense
    ws.append(['', f'Total Expenses: {expense_total}'])
    
    wb.save(response)
    return response
