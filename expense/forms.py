from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):  #You're creating a form based on the Budget model.
    class Meta:
        model = Budget   #"Use the Budget model."
        fields = ["category","monthly_limit"]  #"Generate input fields only for category and monthly_limit."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", "Select Category")] + list(self.fields["category"].choices)