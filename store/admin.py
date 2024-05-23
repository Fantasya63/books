from django.contrib import admin

# Register your models here.
from .models import Account, Book, Category, Order
    
admin.site.register(Account)
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Order)
