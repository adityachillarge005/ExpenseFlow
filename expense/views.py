from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Expense
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout
from django.db.models import Sum

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
        amount = request.POST.get("amount","")
        category = request.POST.get("category","")
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
        all_expenses = Expense.objects.filter(user= request.user)
        total_expenses = all_expenses.aggregate(Sum("amount"))["amount__sum"] or 0
        total_transaction = all_expenses.count()
        search = request.GET.get("search","")
        category_summary = all_expenses.values("category").annotate(
            total = Sum("amount")
        )
        expenses = all_expenses.filter(
            title__icontains = search
        )
        return render(request,
                      "view_expense.html",
                      {
                          "expenses":expenses,
                          "search":search,
                          "total_expenses":total_expenses,
                          "total_transaction":total_transaction,
                          "category_summary":category_summary,
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
    