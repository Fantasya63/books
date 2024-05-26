from django.urls import path
from . import views

app_name = "store"
urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("search/", views.search, name="search"),
    path("cart/", views.cart, name="cart"),
    path("book/<int:bookID>/", views.book, name="book"),
    path("checkout", views.checkout, name="checkout"),
    path("purchases", views.purchases, name="purchases"),
    path("account", views.view_account, name="account")

]