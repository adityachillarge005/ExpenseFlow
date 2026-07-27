from django.db import models
from django.contrib.auth.models import User

# Create your models here.
CATEGORY_CHOICES = [
    ("Food", "Food"),
    ("Transport", "Transport"),
    ("Shopping", "Shopping"),
    ("Bills", "Bills"),
    ("Entertainment", "Entertainment"),
    ("Healthcare", "Healthcare"),
    ("Education", "Education"),
    ("Other", "Other"),
]
class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10 , decimal_places=2)
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    ) 
    date = models.DateField()
    description = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE, 
        related_name="expenses"   
    )

    def __str__(self):
        return self.title


class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets"
    )
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    )
    monthly_limit = models.DecimalField(max_digits=10,decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.category} - ₹{self.monthly_limit}"
  
