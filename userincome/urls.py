from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income),
         name="search_income"),
    path('income-summary/',views.income_summary,name="income-summary"),
    path('get_monthly_data/',views.get_monthly_income,name="get_monthly_data"),
    path('report/',views.report,name="report"),
    path('generate-report/',views.generate_report,name="generate-report"),
    path('export_pdf/', views.export_pdf, name='export_pdf'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_xlsx/', views.export_xlsx, name='export_xlsx'),
    path("monthly-income-data/",views.monthly_income_data,name="monthly_income_data")
]
