from django.urls import path
from .import views
urlpatterns = [
    path("",views.home,name="home"),
    path("add-expense/",views.add_expense,name="add_expense"),
    path("view-expenses/",views.view_expenses,name="view_expense"),
    path("edit-expense/<int:id>/",views.edit_expense,name = "edit_expense"),
    path("delete-expense/<int:id>/",views.delete_expense,name = "delete_expense"),
    path("register/",views.register,name = "register"),
    path("login/",views.user_login,name = "user_login"),
    path("logout/",views.user_logout,name = "user_logout"),
    path("predict_category/",views.predict_category,name = "predict_category"),
]
