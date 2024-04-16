# finances/tasks.py
import redis
from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from expenses.models import Expense
from userincome.models import UserIncome
from django.contrib.auth.models import User
import pandas as pd
import os

@shared_task
def generate_report_and_send_email():
    today = timezone.now()
    end_of_week = today - timezone.timedelta(days=today.weekday()) + timezone.timedelta(days=6)

    if today.day == end_of_week.day:  # If it's the last day of the week
        for user in User.objects.all():  # Loop through each user
            # weekly_expenses = Expense.objects.filter(date__range=[end_of_week - timezone.timedelta(days=6), end_of_week], owner=user)
            weekly_incomes = UserIncome.objects.filter(date__range=[end_of_week - timezone.timedelta(days=6), end_of_week], owner=user)

            # Extract necessary fields
            # weekly_expense_data = list(weekly_expenses.values('description', 'category', 'amount'))
            weekly_income_data = list(weekly_incomes.values('description', 'source', 'amount'))

            # Create DataFrames
            # weekly_expense_df = pd.DataFrame(weekly_expense_data)
            weekly_income_df = pd.DataFrame(weekly_income_data)

            # Save report to Excel file
            weekly_report_path = f'weekly_report_{user.username}.xlsx'
            with pd.ExcelWriter(weekly_report_path) as writer:
                # weekly_expense_df.to_excel(writer, sheet_name='Expenses', index=False)
                weekly_income_df.to_excel(writer, sheet_name='Incomes', index=False)

            # Send email with the weekly report attached
            email = EmailMessage(
                subject='Weekly Financial Report',
                body='Please find attached your weekly financial report.',
                to=[user.email]  # Send only to the current user
            )
            email.attach_file(weekly_report_path)
            email.send()

            # Clean up generated file
            # os.remove(weekly_report_path)

    if today.day == 1:  # If it's the first day of the month
        for user in User.objects.all():  # Loop through each user
            # monthly_expenses = Expense.objects.filter(date__month=today.month, date__year=today.year, owner=user)
            monthly_incomes = UserIncome.objects.filter(date__month=today.month, date__year=today.year, owner=user)

            # Extract necessary fields
            # monthly_expense_data = list(monthly_expenses.values('description', 'category', 'amount'))
            monthly_income_data = list(monthly_incomes.values('description', 'source', 'amount'))

            # Create DataFrames
            # monthly_expense_df = pd.DataFrame(monthly_expense_data)
            monthly_income_df = pd.DataFrame(monthly_income_data)

            # Save report to Excel file
            monthly_report_path = f'monthly_report_{user.username}.xlsx'
            with pd.ExcelWriter(monthly_report_path) as writer:
                # monthly_expense_df.to_excel(writer, sheet_name='Expenses', index=False)
                monthly_income_df.to_excel(writer, sheet_name='Incomes', index=False)

            # Send email with the monthly report attached
            email = EmailMessage(
                subject='Monthly Financial Report',
                body='Please find attached your monthly financial report.',
                to=[user.email]  # Send only to the current user
            )
            email.attach_file(monthly_report_path)
            email.send()

            # Clean up generated file
            # os.remove(monthly_report_path)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Define a function to schedule the task
def schedule_report_sending():
    today = timezone.now()
    if today.day == 1:  # Schedule monthly report on the first day of the month
        redis_client.set('report_schedule', 'monthly')
    elif today.weekday() == 6:  # Schedule weekly report on the last day of the week (Sunday)
        redis_client.set('report_schedule', 'weekly')

# Schedule the task to be run periodically
schedule_report_sending()
