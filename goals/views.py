from django.shortcuts import render, redirect, get_object_or_404
from .models import Goal
from .forms import GoalForm, AddAmountForm
from django.contrib.auth.decorators import login_required



def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_goals')

    form = GoalForm()
    return render(request, 'goals/add_goals.html', {'form': form})

@login_required(login_url='/authentication/login')
def list_goals(request):

    # goals = Goal.objects.all()
    goals = Goal.objects.filter()
    add_amount_form = AddAmountForm() 
    return render(request, 'goals/list_goals.html', {'goals': goals, 'add_amount_form': add_amount_form})

def add_amount(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)

    if request.method == 'POST':
        form = AddAmountForm(request.POST)
        if form.is_valid():
            additional_amount = form.cleaned_data['additional_amount']
            goal.current_saved_amount += additional_amount
            goal.save()
            return redirect('list_goals')

def delete_goal(request, goal_id):
    try:
        goal = Goal.objects.get(id=goal_id)
        goal.delete()
        return redirect('list_goals')
    except Goal.DoesNotExist:
        # Handle goal not found error or any other appropriate action
        pass