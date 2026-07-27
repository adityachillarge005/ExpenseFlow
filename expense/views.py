from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Expense,Budget
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout
from django.db.models import Sum
import os
import pickle
from .forms import BudgetForm
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "trained_models", "vectorizer.pkl")
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

with open(VECTORIZER_PATH, "rb") as file:
    vectorizer = pickle.load(file)
# Create your views here.
def home(request):
    return render(request,"home.html")
    # return HttpResponse(f"Hello {request.user}")

def validate_expense(title, amount, category, date):
    if not title:
        return "Title is required."

    if not amount:
        return "Amount is required."

    if category == "Select":
        return "Please select a category."

    if not date:
        return "Date is required."

    return None

@login_required
def add_expense(request):
    if request.method == "POST":
        title = request.POST.get("title","").strip().title()
        prediction  = model.predict(vectorizer.transform([title]))[0]
        print(prediction)
        amount = request.POST.get("amount","")
        category = prediction
        date = request.POST.get("date","")
        description = request.POST.get("description","").strip()
        error = validate_expense(title, amount, category, date)

        if error:
            messages.error(request, error)
            return redirect("add_expense")

        Expense.objects.create(
            title = title,
            amount = amount,
            category = category,
            date = date,
            description = description,
            user = request.user
        )
        messages.success(request, "Expense added successfully.")
        return redirect("view_expense")
    return render(request,"add_expense.html")

@login_required
def view_expenses(request):
    all_expenses = Expense.objects.filter(user=request.user)

    # Dashboard Statistics
    total_expenses = all_expenses.aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_transaction = all_expenses.count()

    # Search
    search = request.GET.get("search", "")

    expenses = all_expenses.filter(
        title__icontains=search
    )

    # Category Summary
    category_summary = all_expenses.values("category").annotate(
        total=Sum("amount")
    )

    # ==========================
    # Monthly Budget Overview
    # ==========================

    budgets = Budget.objects.filter(user=request.user)

    budget_data = []

    for budget in budgets:

        category_expenses = all_expenses.filter(
            category=budget.category,
            date__month=budget.month,
            date__year=budget.year
        )

        spent = category_expenses.aggregate(
            total=Sum("amount")
        )

        spent_amount = spent["total"] or 0

        remaining = budget.monthly_limit - spent_amount

        if budget.monthly_limit > 0:
            percentage = (spent_amount / budget.monthly_limit) * 100
        else:
            percentage = 0

        display_percentage = min(percentage, 100)

        budget_data.append({
            "category": budget.category,
            "monthly_limit": budget.monthly_limit,
            "spent_amount": spent_amount,
            "remaining": remaining,
            "percentage": percentage,
            "display_percentage": display_percentage,
        })

    return render(
        request,
        "view_expense.html",
        {
            "expenses": expenses,
            "search": search,
            "total_expenses": total_expenses,
            "total_transaction": total_transaction,
            "category_summary": category_summary,
            "budget_data": budget_data,
        }
    )
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(
    Expense,
    id=id,
    user=request.user
)

    if request.method == "POST":
        title = request.POST.get("title", "").strip().title()
        amount = request.POST.get("amount", "")
        category = request.POST.get("category", "")
        date = request.POST.get("date", "")
        description = request.POST.get("description", "").strip()

        error = validate_expense(title, amount, category, date)

        if error:
            messages.error(request, error)
            return redirect("edit_expense", id=id)

        expense.title = title
        expense.amount = amount
        expense.category = category
        expense.date = date
        expense.description = description

        expense.save()

        messages.success(request, "Expense updated successfully.")
        return redirect("view_expense")

    return render(
        request,
        "edit_expense.html",
        {
            "expense": expense
        }
    )
            
@login_required         
def delete_expense(request, id):
    expense = get_object_or_404(Expense,id=id,user = request.user)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect("view_expense")

    return render(
        request,
        "delete_expense.html",
        {
            "expense": expense
        }
    )


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("home")
        
    else:
         form = UserCreationForm()
         
    return render(request,"register.html",{
         "form":form
        }
    )

def user_login(request):
    if request.method == "POST":
          form = AuthenticationForm(request,request.POST)
          if form.is_valid():
            user = form.get_user()
            login(request,user)
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            
            return redirect("home")
    else:
        form = AuthenticationForm(request)


    return render(request,"login.html",{
         "form":form
        }
    )

def user_logout(request):
    if request.method=="POST":
        logout(request)
        return redirect("user_login")


def predict_category(request):
    title = request.GET.get("title", "").strip()

    prediction = model.predict(vectorizer.transform([title]))[0]

    descriptions = {
        "Food": f"Food purchase: {title}.",
        "Transport": f"Transportation expense: {title}.",
        "Entertainment": f"Entertainment expense: {title}.",
        "Shopping": f"Shopping expense: {title}.",
        "Bills": f"Bill payment: {title}.",
    }

    description = descriptions.get(
        prediction,
        f"Expense for {title}."
    )

    return JsonResponse({
        "category": prediction,
        "description": description
    })
    
from datetime import datetime

@login_required
def set_budget(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)

        if form.is_valid():
            # Create budget object without saving
            budget = form.save(commit=False)

            # Fill remaining fields
            budget.user = request.user
            now = datetime.now()
            budget.month = now.month
            budget.year = now.year

            # Check if budget already exists
            existing_budget = Budget.objects.filter(
                user=request.user,
                category=budget.category,
                month=budget.month,
                year=budget.year
            ).first()

            if existing_budget:
                existing_budget.monthly_limit = budget.monthly_limit
                existing_budget.save()
                messages.success(request, "Budget updated successfully.")
            else:
                budget.save()
                messages.success(request, "Budget created successfully.")

            return redirect("view_expense")

        # Form is invalid
        messages.error(request, "Please correct the errors below.")

    else:
        form = BudgetForm()

    return render(
        request,
        "set_budget.html",
        {
            "form": form
        }
    )

# @login_required
# def budget_dashboard(request):
#     budgets = Budget.objects.filter(user = request.user)

#     budget_data = []
#     for budget in budgets:
#         expenses = Expense.objects.filter(
#             user=request.user,
#             category=budget.category,
#             date__month=budget.month,
#             date__year=budget.year
#         )
#         spent = expenses.aggregate(total = Sum("amount"))
#         spent_amount = spent["total"] or 0
#         remaining = budget.monthly_limit - spent_amount
#         if budget.monthly_limit>0:
#             percentage = (spent_amount/budget.monthly_limit)*100
#         else:
#             percentage = 0

#         budget_data.append({
#             "category":budget.category,
#             "monthly_limit":budget.monthly_limit,
#             "spent_amount":spent_amount,
#             "remaining":remaining,
#             "percentage":percentage
#         })

#     return render(request,"budget_dashboard.html",{"budget_data":budget_data})
        